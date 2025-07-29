# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Watching an engine session.
"""
import datetime
import json
import logging
import os
import threading
import time
import traceback
import typing as t

import hallyd

import krrez.flow.graph.visualizer
import krrez.flow.logging
import krrez.flow.writer

_logger = logging.getLogger(__name__)


class Watch:
    """
    Watches a :py:class:`krrez.flow.Session`, e.g. in order to make it visible to the user.

    Each session is associated to an execution of a :py:class:`krrez.flow.runner.Engine`.
    The data that it reads is written by a :py:class:`krrez.flow.writer.Writer`.

    The actual watching occurs only in activated state, which is inside a :code:`with` block. You can access all
    properties even without ever having the watch activated, but refresh only takes place while activated, and handlers
    will be called only then as well (this even means: you might never receive any log messages or similar before
    activating, as they come via a handler).
    """

    def __init__(self, session: krrez.flow.Session, *,
                 log_block_arrived_handler=None,
                 log_block_changed_handler=None,
                 status_changed_handler=None,
                 bit_graph_image_changed_handler=None):
        """
        :param session: The session to watch.
        """
        self.__log_files = {}
        self.__session = session
        self.__entered = 0
        self.__log_block_arrived_handler = log_block_arrived_handler
        self.__log_block_changed_handler = log_block_changed_handler
        self.__status_changed_handler = status_changed_handler
        self.__bit_graph_image_changed_handler = bit_graph_image_changed_handler
        self.__chosen_bits = session.path("chosen_bits").read_text().split("\n")
        self.__began_at = datetime.datetime.fromisoformat((session.path("began_at")).read_text())
        self.__process_permanent_id = session.path("process_permanent_id").read_text()
        self.__all_install_bits = None
        self.__installing_bits = []
        self.__installed_bits = []
        self.__ended_at = None
        self.__failed_info = None
        self.__base_dir_monitor = None
        self.__all_install_bits_monitor = None
        self.__log_dir_monitor = None
        self.__refresh_bit_graph_image__invalid = False
        self.__refresh_bit_graph_image__processing = False
        self.__refresh_bit_graph_image__lock = threading.Lock()
        self.__all_install_bits_lock = threading.RLock()
        self.__check_base_directory(init_phase=True)

    def __enter__(self):
        if not self.__entered:
            self.__base_dir_monitor = self.__Monitor(self.__session.path, self.__check_base_directory)
            self.__base_dir_monitor.__enter__()

            threading.Thread(target=self.__execute_handler, args=(self.__status_changed_handler,)).start()

            if self.__log_block_arrived_handler or self.__log_block_changed_handler:
                self.__log_dir_monitor = self.__Monitor(
                    krrez.flow.writer._session_path_to_log_path(self.__session.path), self.__check_log_directory)
                self.__log_dir_monitor.__enter__()

            self.__refresh_bit_graph_image()

        self.__entered += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__entered -= 1
        if not self.__entered:
            self.__stop()

    def abort(self):
        self.__session.path("_do_abort").make_file()

    def wait(self) -> None:
        """
        Block until the session has ended.
        """
        if not self.__entered:
            raise InvalidStateError("this can only be called in an active context ('with' statement)")
        while not self.ended_at:
            time.sleep(1)

    def ensure_successful(self) -> None:
        """
        Block until the session has ended and raise an exception if the session has not finished successfully.
        """
        self.wait()
        if not self.was_successful:
            raise RunFailedError("this run was aborted prematurely due to fatal problems")

    @property
    def session(self) -> krrez.flow.Session:
        """
        The session to watch.
        """
        return self.__session

    @property
    def chosen_bits(self) -> list[str]:
        """
        The Bits chosen by the caller to install.
        """
        return self.__chosen_bits

    @property
    def all_install_bits(self) -> t.Optional[list[str]]:
        """
        All Bits that are to be installed.

        This data might be unavailable at the beginning until the dependency graph computation is finished.
        """
        return self.__all_install_bits

    @property
    def began_at(self) -> datetime.datetime:
        """
        This session's start time.
        """
        return self.__began_at

    @property
    def ended_at(self) -> t.Optional[datetime.datetime]:
        """
        This session's stop time (or :code:`None` if currently running).
        """
        return self.__ended_at

    @property
    def was_successful(self) -> bool:
        """
        Whether this session has finished successfully.
        """
        return self.__ended_at and self.__failed_info is None

    @property
    def state_text(self) -> str:
        """
        A human-readable text that describes the current state and when the session began or ended.
        """
        if self.ended_at:
            if self.was_successful:
                return f"Succeeded on {self.__time_text(self.ended_at)}."
            else:
                return f"Failed on {self.__time_text(self.ended_at)}."
        else:
            return f"Running since {self.__time_text(self.began_at)}."

    @property
    def _was_killed(self) -> bool:
        """
        Whether this session was killed (e.g. due to system shutdown).
        """
        return self.__failed_info == "found non-alive"

    @property
    def installing_bits(self) -> list[str]:
        """
        The Bits that currently get applied.
        """
        return self.__installing_bits or []

    @property
    def installed_bits(self) -> list[str]:
        """
        The Bits that were already applied during this run.
        """
        return self.__installed_bits or []

    @property
    def progress(self) -> float:
        """
        The current progress, as value between 0 and 1.
        """
        if self.all_install_bits is None:
            return 0
        return (len(self.installed_bits) + 1) / (len(self.all_install_bits) + 1)

    def __check_base_directory(self, *, init_phase: bool = False):
        self.__check_all_install_bits_directory(init_phase=init_phase)

        if not init_phase:
            self.__refresh_bit_graph_image()

        if not init_phase and self.__base_dir_monitor:
            install_bits_dir = self.__session.path(krrez.flow.writer.Writer.ALL_INSTALL_BITS_DIR_NAME)
            if not self.__all_install_bits_monitor and install_bits_dir.exists():
                self.__all_install_bits_monitor = self.__Monitor(install_bits_dir,
                                                                 self.__check_all_install_bits_directory)
                self.__all_install_bits_monitor.__enter__()

        if not self.ended_at:
            if (ended_at_file := self.__session.path(krrez.flow.writer.Writer.ENDED_AT_FILE_NAME)).exists():
                failed_file = self.__session.path(krrez.flow.writer.Writer.FAILED_FILE_NAME)
                failed_info = failed_file.read_text() if failed_file.exists() else None
                self.__set_ended_status(failed_info,
                                        datetime.datetime.fromisoformat(ended_at_file.read_text()),
                                        init_phase=init_phase)

    def __check_all_install_bits_directory(self, *, init_phase: bool = False):
        self.__check_alive(init_phase=init_phase)

        with self.__all_install_bits_lock:
            install_bits_dir = self.__session.path(krrez.flow.writer.Writer.ALL_INSTALL_BITS_DIR_NAME)
            if install_bits_dir.exists():
                if self.all_install_bits is None:
                    self.__set_all_install_bits_status([c.name for c in install_bits_dir.iterdir()], init_phase=init_phase)
                installing_bits = []
                installed_bits = []
                for install_bit in self.all_install_bits:
                    state = install_bits_dir(install_bit).stat().st_size
                    if state == 1:
                        installing_bits.append(install_bit)
                    elif state == 2:
                        installed_bits.append(install_bit)
                    elif state > 2:
                        raise RuntimeError("there is an invalid state file in all_install_bits")
                self.__set_bits_status(installing_bits, installed_bits, init_phase=init_phase)

    def __check_alive(self, *, init_phase: bool = False):
        import krrez.seeding  # TODO
        if isinstance(self.__session.context, krrez.seeding._RemoteContext):
            return  # TODO

        if hallyd.subprocess.is_process_running(self.__process_permanent_id) is False:
            if self.__session.path(krrez.flow.writer.Writer.ENDED_AT_FILE_NAME).exists():  # TODO odd
                return

            failed_info = "found non-alive"
            try:
                self.__session.path(krrez.flow.writer.Writer.FAILED_FILE_NAME).write_text(failed_info)
                self.__session.path(krrez.flow.writer.Writer.ENDED_AT_FILE_NAME).write_text(
                    datetime.datetime.now().isoformat())
            except IOError:
                _logger.debug(traceback.format_exc())
            self.__set_ended_status(failed_info, datetime.datetime.now(), init_phase=init_phase)

    def __check_log_directory(self):
        log_files = list(sorted(krrez.flow.writer._session_path_to_log_path(self.__session.path).iterdir()))

        for name, log_file in list(self.__log_files.items()):
            if log_file:
                if log_file.is_finished:
                    self.__log_files[name] = None
                else:
                    log_file.update()

        for log_file_path in log_files:
            if log_file_path.name not in self.__log_files:
                log_file = self.__log_files[log_file_path.name] = self.__LogFile(log_file_path, self.__add_log_block,
                                                                                 self.__log_block_changed)
                log_file.update()

    def __add_log_block(self, block_id, message, began_at, only_single_time, severity):
        parent_block_id = block_id.rpartition("/")[0]

        self.__execute_handler(self.__log_block_arrived_handler,
                               parent_block_id, block_id, message, began_at, only_single_time, severity)

    def __log_block_changed(self, block_id, ended_at):
        self.__execute_handler(self.__log_block_changed_handler, block_id, ended_at)

    def __set_bits_status(self, installing_bits, installed_bits, *, init_phase: bool):
        installing_bits, installed_bits = sorted(installing_bits), sorted(installed_bits)
        if self.installing_bits != installing_bits or self.installed_bits != installed_bits:
            self.__installing_bits = installing_bits
            self.__installed_bits = installed_bits
            if not init_phase:
                self.__execute_handler(self.__status_changed_handler)

    def __set_all_install_bits_status(self, all_install_bits, *, init_phase: bool):
        self.__all_install_bits = all_install_bits
        if not init_phase:
            self.__execute_handler(self.__status_changed_handler)

    def __set_ended_status(self, failed_info, ended_at, *, init_phase: bool):
        self.__failed_info = failed_info
        self.__ended_at = ended_at

        if not init_phase:
            def _stop():
                if ended_at:
                    self.__stop()
                self.__execute_handler(self.__status_changed_handler)
            threading.Thread(target=_stop).start()

    def __execute_handler(self, handler, *args):
        if handler:
            handler(*args)

    def __stop(self):
        monitors = filter(None, [self.__base_dir_monitor, self.__all_install_bits_monitor, self.__log_dir_monitor])
        self.__base_dir_monitor = self.__all_install_bits_monitor = self.__log_dir_monitor = None
        for monitor in monitors:
            monitor.check_if_changed()
            monitor.__exit__(None, None, None)

    def __refresh_bit_graph_image(self):
        with self.__refresh_bit_graph_image__lock:
            with self.__all_install_bits_lock:
                if self.__bit_graph_image_changed_handler and (self.__installing_bits is not None):
                    if self.__refresh_bit_graph_image__processing:
                        self.__refresh_bit_graph_image__invalid = True
                    else:
                        threading.Thread(target=self.__refresh_bit_graph_image__process).start()
                        self.__refresh_bit_graph_image__processing = True

    def __refresh_bit_graph_image__process(self):
        graph_path = self.__session.path(krrez.flow.writer.Writer.BIT_GRAPH_FILE_NAME)
        bit_graph_image_svg = None

        if graph_path.is_file():
            try:
                graph_data = hallyd.bindle.loads(graph_path.read_text())
            except Exception:
                graph_data = None
                
            if graph_data:
                graph = graph_data["graph"]
                extra_data = graph_data["extra_data"]
                bit_graph_image_svg = krrez.flow.graph.visualizer.try_dump_pygraphviz(graph, extra_data)
        
        with self.__refresh_bit_graph_image__lock:
            if bit_graph_image_svg:
                self.__execute_handler(self.__bit_graph_image_changed_handler, bit_graph_image_svg)
            if self.__refresh_bit_graph_image__invalid:
                self.__refresh_bit_graph_image__invalid = False
                threading.Thread(target=self.__refresh_bit_graph_image__process).start()
            else:
                self.__refresh_bit_graph_image__processing = False

    @staticmethod
    def __time_text(atime):
        return atime.strftime("%c").strip()  # sometimes there is a space in the end; we don't want that

    class __Monitor(hallyd.fs_monitor.FilesystemMonitor):

        def __init__(self, path: hallyd.fs.Path, on_changed_func: t.Callable[[], None]):
            super().__init__(path)
            self.__on_changed_func = on_changed_func

        def _changed(self):
            self.__on_changed_func()

    # noinspection PyProtectedMember
    class __LogFile:

        def __init__(self, path: hallyd.fs.Path, add_log_block_func, log_block_changed_func):
            self.__add_log_block_func = add_log_block_func
            self.__log_block_changed_func = log_block_changed_func
            self.__file_path = path
            self.__root_prefix = ""
            self.__read_after = 0
            self.__buffer = b""
            self.__initialized = False

        @property
        def is_finished(self):
            return self.__buffer is None

        def update(self):
            while not self.is_finished and (not self.__initialized
                                            or os.stat(self.__file_path).st_size > self.__read_after):

                with open(self.__file_path, "rb") as f:
                    f.seek(self.__read_after)
                    new_content = f.read()
                self.__buffer += new_content
                self.__read_after += len(new_content)

                while self.__buffer:
                    next_linebreak = self.__buffer.find(b"\n")

                    if next_linebreak == 0:
                        self.__buffer = None

                    elif next_linebreak > 0:
                        line = self.__buffer[:next_linebreak].decode()

                        data_ended_at = hallyd.lang.match_format_string(
                            krrez.flow.writer.Writer.ENDED_AT_PATTERN, line)
                        if data_ended_at:
                            ended_at = data_ended_at["ended_at"]
                            block_id = self.__root_prefix + data_ended_at["block_id"]
                            self.__log_block_changed_func(block_id, datetime.datetime.fromisoformat(ended_at))
                            self.__buffer = self.__buffer[next_linebreak + 1:]
                            continue

                        data_block_id_prefix = hallyd.lang.match_format_string(
                            krrez.flow.writer.Writer.PREFIX_PATTERN, line)
                        if data_block_id_prefix:
                            self.__root_prefix = data_block_id_prefix["prefix"]
                            self.__buffer = self.__buffer[next_linebreak + 1:]
                            continue

                        next_linebreak_after = self.__buffer.find(b"\n", next_linebreak + 1)
                        if next_linebreak_after == -1:
                            break
                        line2 = self.__buffer[next_linebreak + 1:next_linebreak_after].decode()
                        msg = json.loads('"' + line2[1:] + '"')
                        ts = line[:krrez.flow.writer.Writer.ISO_FORMAT_LENGTH].strip()
                        te = line[krrez.flow.writer.Writer.ISO_FORMAT_LENGTH:][:2].strip()
                        sev = line[krrez.flow.writer.Writer.ISO_FORMAT_LENGTH + 8:][:10].strip()
                        z = line[krrez.flow.writer.Writer.ISO_FORMAT_LENGTH + 8 + 12:]
                        self.__add_log_block_func(self.__root_prefix + z, msg, datetime.datetime.fromisoformat(ts),
                                                  not te, getattr(krrez.flow.logging.Severity, sev))
                        self.__initialized = True
                        self.__buffer = self.__buffer[next_linebreak_after + 1:]

                    else:
                        break


class RunFailedError(RuntimeError):
    """
    Errors during the session runtime.
    """


class InvalidStateError(Exception):
    """
    Watch is in an invalid state.
    """
