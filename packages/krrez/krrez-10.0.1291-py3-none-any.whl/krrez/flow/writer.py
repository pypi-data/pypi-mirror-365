# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Engine session writer.
"""
import contextlib
import datetime
import json
import os
import sys
import typing as t

import hallyd

import krrez.api
import krrez.flow.bit_loader
import krrez.flow.dialog
import krrez.flow.graph
import krrez.flow.logging
import krrez.flow.runner


def _session_path_to_log_path(path: hallyd.fs.Path) -> hallyd.fs.Path:
    return path("log")


class Writer:
    """
    Write state and logging data for a :py:class:`krrez.flow.Session`.

    Each session is associated to an execution of a :py:class:`krrez.flow.runner.Engine`.
    The data that it writes is read by a :py:class:`krrez.flow.watch.Watch`.

    The session is considered to be active within the activation period of this writer, i.e. in its :code:`with` block.
    """

    ISO_FORMAT_LENGTH = 26
    PREFIX_PATTERN = "prefix: {prefix}"
    ENDED_AT_PATTERN = "ended at {ended_at}: {block_id}"

    BIT_GRAPH_FILE_NAME = "bit_graph"
    ALL_INSTALL_BITS_DIR_NAME = "all_install_bits"
    FAILED_FILE_NAME = "failed"
    ENDED_AT_FILE_NAME = "ended_at"

    class LogBlock(krrez.flow.logging.Logger):

        class BlockLoggerMode(krrez.flow.logging.LoggerMode[t.ContextManager["Logger"]]):

            def __init__(self, log_block):
                self.__log_block = log_block

            def _log(self, message, severity, aux_name):
                return Writer.LogBlock(message=message or "Executing some inner steps.", severity=severity,
                                       session=self.__log_block.session,
                                       aux_name=aux_name or self.__log_block.aux_name, is_root=False,
                                       path=f"{self.__log_block.path}/{hallyd.lang.unique_id()}_{aux_name}")

        class MessageLoggerMode(krrez.flow.logging.LoggerMode[None]):

            def __init__(self, log_block):
                self.__log_block = log_block

            def _log(self, message, severity, aux_name):
                with Writer.LogBlock(message=message, severity=severity, session=self.__log_block.session,
                                     aux_name=aux_name or self.__log_block.aux_name, is_root=False,
                                     path=f"{self.__log_block.path}/{hallyd.lang.unique_id()}_{aux_name}",
                                     only_single_time=True):
                    pass

        def __init__(self, *, message: str, path: str, aux_name: str, severity: krrez.flow.logging.Severity,
                     only_single_time: bool = False,
                     is_root: bool, session: "krrez.flow.Session"):
            message = str(message)
            self.__message = message
            self.__path = path
            self.__aux_name = aux_name
            self.__only_single_time = only_single_time
            self.__is_root = is_root
            self.__session = session
            self.__log_path = _session_path_to_log_path(session.path)
            self.__my_file_path = self.__log_path(f"m{self.__path.rpartition('/')[2]}")

            if not is_root:
                parent_path = self.__log_path(f"m{self.__path.rpartition('/')[0].rpartition('/')[2]}")
                if not parent_path.exists():
                    with open(parent_path, "x") as f:
                        f.write(Writer.PREFIX_PATTERN.format(prefix=self.__path.rpartition('/')[0] + "/") + "\n")

                with open(parent_path, "a") as f:
                    f.write(datetime.datetime.now().isoformat().ljust(Writer.ISO_FORMAT_LENGTH, " "))
                    f.write("      " if only_single_time else " - ...")
                    f.write("  " + severity.name.ljust(10, " "))
                    f.write("  " + self.__path.rpartition('/')[2])
                    f.write(f"\n {json.dumps(message)[1:-1]}\n")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if not (self.__is_root or self.__only_single_time):
                parent_path = self.__log_path(f"m{self.__path.rpartition('/')[0].rpartition('/')[2]}")
                with open(parent_path, "a") as f:
                    f.write(Writer.ENDED_AT_PATTERN.format(
                        ended_at=datetime.datetime.now().isoformat().ljust(Writer.ISO_FORMAT_LENGTH, " "),
                        block_id=self.__path.rpartition('/')[2]) + "\n")

            if self.__my_file_path.exists():
                with open(self.__my_file_path, "a") as f:
                    f.write("\n")

        @property
        def path(self) -> str:
            return self.__path

        @property
        def aux_name(self) -> str:
            return self.__aux_name

        @property
        def session(self):
            return self.__session

        @property
        def block(self):
            return Writer.LogBlock.BlockLoggerMode(self)

        @property
        def message(self):
            return Writer.LogBlock.MessageLoggerMode(self)

    class _ApplyBitLogBlock(LogBlock):

        def __init__(self, *args, bit_name, orig_session, **kwargs):
            super().__init__(*args, **kwargs)
            self.__signal_file_path = orig_session.path(Writer.ALL_INSTALL_BITS_DIR_NAME, bit_name)

        def __enter__(self):
            with open(self.__signal_file_path, "a") as f:
                f.write("i")
            return super().__enter__()

        def __exit__(self, exc_type, exc_val, exc_tb):
            super().__exit__(exc_type, exc_val, exc_tb)
            with open(self.__signal_file_path, "a") as f:
                f.write("i")

    def __init__(self, *, session: "krrez.flow.Session", log_block: t.Optional["Writer.LogBlock"],
                 chosen_bits: list[type["krrez.api.Bit"]], apply_message_func: t.Callable[[str], str]):
        self.__session = session
        self.__is_redirected = log_block is not None
        self.__chosen_bits = chosen_bits
        self.__apply_message_func = apply_message_func
        # noinspection PyTypeChecker
        self.__log_block = log_block or Writer.LogBlock(message="", severity=None, path="", aux_name="root",
                                                        session=session, only_single_time=False, is_root=True)
        self.__dialog_hub_foo1 = None
        self.__dialog_hub_foo2 = None
        self.__dialog_hub_foo3 = None
        self.__config_ref = None
        self.__hub: t.Optional[krrez.flow.dialog.Hub] = None
        self.__refresh_bit_graph__last_installing_bits = None
        self.__refresh_bit_graph__last_installed_bits = None
        self.__refresh_bit_graph__last_failed_bits = None

    @property
    def dialog_hub_path(self) -> hallyd.fs.Path:
        return self.__dialog_hub_foo1

    @property
    def dialog(self) -> krrez.flow.dialog.Endpoint:
        return krrez.flow.dialog.HubEndpoint(self.__dialog_hub_foo2)

    def __enter__(self):
        session_temp_path: hallyd.fs.Path = self.__session.path2
        session_temp_path.make_dir(readable_by_all=True)
        session_temp_path("log").make_dir(readable_by_all=True)
        session_temp_path("chosen_bits").write_text("\n".join([krrez.flow.bit_loader.bit_name(bit)
                                                               for bit in self.__chosen_bits]))
        session_temp_path("began_at").write_text(datetime.datetime.now().isoformat())
        session_temp_path("process_permanent_id").write_text(
            hallyd.subprocess.process_permanent_id_for_pid(os.getpid()))
        try:
            if self.__is_redirected:
                self.__dialog_hub_foo1 = _ipc_dialog_hub_object_path(self.__log_block.session.path)
                _ipc_dialog_hub_object_path(session_temp_path).symlink_to(self.__dialog_hub_foo1)
                self.__dialog_hub_foo2 = hallyd.ipc.client(self.__dialog_hub_foo1)
            else:
                self.__hub = krrez.flow.dialog.Hub(_ipc_dialog_hub_path(session_temp_path))
                self.__hub.__enter__()
                self.__dialog_hub_foo1 = _ipc_dialog_hub_object_path(session_temp_path)
                self.__dialog_hub_foo2 = self.__hub
                self.__dialog_hub_foo3 = hallyd.ipc.threaded_server(self.__hub, path=self.__dialog_hub_foo1)
                self.__dialog_hub_foo3.enable()
            self.__config_ref = krrez.flow.config.new_config_server_for_session(session_temp_path)
            self.__config_ref.enable()
            self.__session.path.symlink_to(session_temp_path.relative_to(self.__session.path.parent, strict=False))
            self.__log_block.__enter__()
            return self
        except:
            self.__exit__(*sys.exc_info())
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__dialog_hub_foo3:
            self.__dialog_hub_foo3.disable()
        if self.__config_ref:
            self.__config_ref.disable()
        if self.__hub:
            self.__hub.__exit__(exc_type, exc_val, exc_tb)
        self.__stop()

    def set_install_bits(self, install_bits: t.Iterable[type["krrez.api.Bit"]]) -> None:
        """
        Set the Bits that are to be applied in this session.

        :param install_bits: The Bits.
        """
        all_install_bits_dir_path = self.__session.path(Writer.ALL_INSTALL_BITS_DIR_NAME)
        all_install_bits_dir_temp_path = hallyd.fs.Path(f"{all_install_bits_dir_path}~")
        all_install_bits_dir_temp_path.make_dir(readable_by_all=True)
        for bit in install_bits:
            all_install_bits_dir_temp_path(krrez.flow.bit_loader.bit_name(bit)).write_text("")
        all_install_bits_dir_temp_path.rename(all_install_bits_dir_path)

    def refresh_bit_graph(self, installing_bits: list[type["krrez.api.Bit"]],
                          installed_bits: list[type["krrez.api.Bit"]], failed_bits: list[type["krrez.api.Bit"]],
                          bit_graph: "krrez.flow.graph.Node") -> None:
        """
        Refresh the Bit graph.

        :param installing_bits: The Bits that get applied at the moment.
        :param installed_bits: The Bits that got applied.
        :param failed_bits: The Bits that failed.
        :param bit_graph: The Bit graph.
        """
        if (installing_bits == self.__refresh_bit_graph__last_installing_bits
                and installed_bits == self.__refresh_bit_graph__last_installed_bits
                and failed_bits == self.__refresh_bit_graph__last_failed_bits):
            return

        self.__refresh_bit_graph__last_installing_bits = list(installing_bits)
        self.__refresh_bit_graph__last_installed_bits = list(installed_bits)
        self.__refresh_bit_graph__last_failed_bits = list(failed_bits)

        def state_string_for_bit(bit: type["krrez.api.Bit"]):
            if bit in failed_bits:
                return "f"
            if bit in installing_bits:
                return "i"
            if bit in installed_bits:
                return "s"

        temp_dir = self.__session.path("temp").make_dir(exist_ok=True, readable_by_all=True)
        bit_graph_file = self.__session.path(Writer.BIT_GRAPH_FILE_NAME)
        bit_graph_temp_file = temp_dir(f"{Writer.BIT_GRAPH_FILE_NAME}~")

        extra_data = {}
        for node in bit_graph.all_descendants():
            node_extra_data = state_string_for_bit(node.bit)
            if node_extra_data:
                extra_data[krrez.flow.bit_loader.bit_name(node.bit)] = node_extra_data
        bit_graph_temp_file.write_text(
            hallyd.bindle.dumps(dict(graph=bit_graph, extra_data=extra_data)))
        bit_graph_temp_file.rename(bit_graph_file)

    def finish(self, *, success: bool) -> None:
        """
        Mark this run as finished (successfully or not).

        :param success: Whether it was successful.
        """
        if not success:
            self.__session.path(Writer.FAILED_FILE_NAME).make_file()
        self.__stop()

    def __stop(self):
        ended_at_path = self.__session.path(Writer.ENDED_AT_FILE_NAME)

        if ended_at_path.exists():
            return

        if self.__log_block:
            self.__log_block.__exit__(None, None, None)

        ended_at_temp_path = self.__session.path(f"{Writer.ENDED_AT_FILE_NAME}~")
        ended_at_temp_path.write_text(datetime.datetime.now().isoformat())
        ended_at_temp_path.rename(ended_at_path)

    def module_log(self, bit_name: str) -> LogBlock:
        """
        A new log block for a Bit.

        :param bit_name: The Bit name.
        """
        return Writer._ApplyBitLogBlock(message=self.__apply_message_func(bit_name),
                                        severity=krrez.flow.logging.Severity.INFO, session=self.__log_block.session,
                                        aux_name=bit_name, is_root=False, bit_name=bit_name,
                                        orig_session=self.__session,
                                        path=f"{self.__log_block.path}/{hallyd.lang.unique_id()}_{bit_name}")

    @property
    def root_log(self) -> LogBlock:
        """
        This session's root log block.
        """
        return self.__log_block


def _ipc_dialog_hub_path(session_path: hallyd.fs.Path) -> hallyd.fs.Path:
    return session_path("ipc_dialog_hub")


def _ipc_dialog_hub_object_path(session_path: hallyd.fs.Path) -> hallyd.fs.Path:
    return session_path("ipc_dialog_hub_object")
