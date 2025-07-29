# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
The engine.
"""
import contextlib
import pickle
import signal
import subprocess
import threading
import time
import traceback
import typing as t

import hallyd

import krrez.coding
import krrez.api
import krrez.flow.bit_loader
import krrez.flow.dialog
import krrez.flow.graph.resolver
import krrez.flow.logging
import krrez.flow.watch
import krrez.flow.writer


class Engine:
    """
    Mechanism that applies (i.e. "installs") some Bits to the current system.

    It handles dependency resolution internally. It holds an internal :py:class`krrez.flow.writer.Writer` for each run
    that feeds a listen and control interface with data, which can be consumed by a
    :py:class:`krrez.flow.watch.Watch`. It can be customized for special cases by subclassing.
    """

    _worker_pool_size = 1

    def start(self, *, context: "krrez.flow.Context", bit_names: t.Iterable[str],
              log_block: t.Optional["krrez.flow.writer.Writer.LogBlock"] = None) -> "krrez.flow.watch.Watch":
        """
        Starts the applying procedure for a given list of Bits.

        :param context: The context.
        :param bit_names: The list of Bits to install.
        :param log_block: The optional log block (from another session) to use as root log block.
        """
        session = krrez.flow.Session.create(context=context)

        hallyd.subprocess.start_function_in_new_process(
            Engine._start_helper_s, kwargs=dict(
                session_name=session.name, context_root_path=context.path,
                bit_names=bit_names, pickled_engine=pickle.dumps(self),
                pickled_log_block=pickle.dumps(log_block),
            ))

        while not session.exists:
            time.sleep(0.25)

        return krrez.flow.watch.Watch(session)

    @staticmethod
    def _start_helper_s(*, pickled_engine, session_name, context_root_path, bit_names, pickled_log_block):
        hallyd.cleanup.mark_current_process_as_cleanup_scope()
        context = krrez.flow.Context(context_root_path)

        # noinspection PyProtectedMember
        pickle.loads(pickled_engine)._start_helper(context=context, bit_names=bit_names,
                                                   log_block=pickle.loads(pickled_log_block),
                                                   session_name=session_name)

    def _start_helper(self, *, context: krrez.flow.Context, bit_names: t.List[str], session_name,
                      log_block: t.Optional["krrez.flow.writer.Writer.LogBlock"]) -> None:
        chosen_bits = [krrez.flow.bit_loader.bit_by_name(mn) for mn in set(bit_names)]
        session = krrez.flow.Session.by_name(session_name, context=context)
        with krrez.flow.writer.Writer(session=session, log_block=log_block, chosen_bits=chosen_bits,
                                      apply_message_func=self._apply_message) as runner_writer:
            with self.__engine_lock(context, runner_writer):
                try:
                    try:
                        with runner_writer.root_log.block.info("Preparing."):
                            install_bits_graph, install_bits = self.__compute_bit_graph(context, runner_writer,
                                                                                        chosen_bits)
                            runner_writer.set_install_bits(install_bits)
                            self._do_prepare(session, install_bits)
                        worker_loop = self._WorkerLoop(self, runner_writer, install_bits_graph, install_bits, context,
                                                       session)
                        worker_loop.run()
                        success = worker_loop.was_successful
                    except Exception as ex:
                        runner_writer.root_log.message.debug(traceback.format_exc())
                        runner_writer.root_log.message.fatal(str(ex))
                        success = False
                        raise
                finally:
                    runner_writer.finish(success=success)
                    self._do_finish(session, runner_writer, success)
                    time.sleep(5)  # TODO

    def _do_finish(self, session: krrez.flow.Session, runner_writer: "krrez.flow.writer.Writer", success: bool) -> None:
        pass

    def _do_prepare(self, session: krrez.flow.Session, install_bits) -> None:
        pass

    def _apply_message(self, bit_name: str) -> str:
        return f"Applying {bit_name}."

    @contextlib.contextmanager
    def __engine_lock(self, context, runner_writer: "krrez.flow.writer.Writer"):
        lock = context.lock("active", ns=Engine)
        lock_timeout = 1
        while not lock.acquire(timeout=lock_timeout):
            lock_timeout = 60 * 20
            runner_writer.root_log.message.info("Waiting for another Krrez run to finish.")
        try:
            yield
        finally:
            lock.release()

    def __compute_bit_graph(self, context, runner_writer: "krrez.flow.writer.Writer",
                            chosen_bits: t.Iterable[type["krrez.api.Bit"]]):
        bit_graph = krrez.flow.graph.resolver.graph_for_bits(chosen_bits)
        already_installed_bits = set(context.installed_bits())
        bit_graph.condense(exclude_if=lambda node: node.bit and krrez.flow.bit_loader.bit_name(node.bit)
                                                   in already_installed_bits)
        return bit_graph, [node.bit for node in bit_graph.all_descendants()]

    class _WorkerLoop:

        def __init__(self, engine: "Engine", runner_writer: "krrez.flow.writer.Writer", bit_graph,
                     install_bits: list[type["krrez.api.Bit"]], context, session):
            self.__engine = engine
            self.__runner_writer = runner_writer
            self.__bit_graph = bit_graph
            self.__install_bits = tuple(install_bits)
            self.__context = context
            self.__session = session
            self.__failed_bits: list[type["krrez.api.Bit"]] = []
            self.__installed_bits: list[type["krrez.api.Bit"]] = []
            self.__installing_bits: list[type["krrez.api.Bit"]] = []

        def __installable_bits(self, bit_graph: "krrez.flow.graph.Node",
                               installed_bits: list[type["krrez.api.Bit"]]) -> list[type["krrez.api.Bit"]]:
            installed_nodes = [bit_graph.node_for_bit(bit) for bit in installed_bits]
            return sorted([node.bit for node in bit_graph.nodes_reachable_from(installed_nodes)
                           if node.bit not in self.__installing_bits
                           and node.bit not in self.__failed_bits],
                          key=lambda bit: krrez.flow.bit_loader.bit_name(bit))

        def __refresh_bit_graph(self):
            self.__runner_writer.refresh_bit_graph(self.__installing_bits, self.__installed_bits,
                                                       self.failed_bits, self.__bit_graph)

        def __start_worker(self, bit: type["krrez.api.Bit"]) -> "_ApplyTask":
            self.__installing_bits.append(bit)
            self.__refresh_bit_graph()
            log_block = self.__runner_writer.module_log(krrez.flow.bit_loader.bit_name(bit))
            log_block.__enter__()
            return self.__engine._do_install_bit(bit, log_block, self.__session, self.__runner_writer)

        def __finish_worker(self, worker: "_ApplyTask") -> None:
            worker.log_block.__exit__(None, None, None)
            self.__installing_bits.remove(worker.bit)
            if worker.error:
                self.__failed_bits.append(worker.bit)
                raise WasInterruptedError()
            else:
                self.__installed_bits.append(worker.bit)
                # noinspection PyProtectedMember
                self.__context._mark_bit_installed(worker.bit)

        @property
        def failed_bits(self) -> list[type["krrez.api.Bit"]]:
            return list(self.__failed_bits)

        @property
        def is_running(self) -> bool:
            return (len(self.__installed_bits) != len(self.__install_bits)) and (len(self.__failed_bits) == 0)

        @property
        def was_successful(self) -> t.Optional[bool]:
            if not self.is_running:
                return len(self.__installed_bits) == len(self.__install_bits)

        def run(self) -> None:
            running_workers = []
            try:
                while self.is_running:
                    installable_bits = None
                    while len(running_workers) < self.__engine._worker_pool_size:
                        installable_bits = installable_bits or \
                                           self.__installable_bits(self.__bit_graph, self.__installed_bits)
                        if not any(installable_bits):
                            break
                        running_workers.append(self.__start_worker(installable_bits.pop(0)))

                    for worker in list(running_workers):
                        if not worker.is_running:
                            running_workers.remove(worker)
                            self.__finish_worker(worker)

                    self.__refresh_bit_graph()

                    if self.__session.path("_do_abort").exists():
                        self.__runner_writer.root_log.message.warning("Run was aborted.")
                        raise WasInterruptedError()

                    time.sleep(0.25)
            except Exception:
                for worker in running_workers:
                    worker.terminate()
                wait_until = time.monotonic() + 2 * 60  # TODO use .monotonic() instead of .time() in other places as well
                for worker in running_workers:
                    if not worker.wait_terminated(wait_until - time.monotonic()):
                        worker.kill()

    def _do_install_bit(self, bit: type["krrez.api.Bit"], log_block, session, runner_writer) -> "_ApplyTask":
        return _ApplyTask(bit, log_block, hallyd.subprocess.start_function_in_new_process(
            Engine._do_install_bit_helper, kwargs=dict(
                context_root_path=session.context.path, session_name=session.name,
                bit_name=krrez.flow.bit_loader.bit_name(bit), dialog_hub_server_ipc_path=runner_writer.dialog_hub_path,
                picked_log_block=pickle.dumps(log_block)
             ), capture_output=True))

    @staticmethod
    def _do_install_bit_helper(*, context_root_path: hallyd.fs.Path, session_name: str, bit_name: str,
                               picked_log_block: bytes, dialog_hub_server_ipc_path: hallyd.fs.Path):
        context = krrez.flow.Context(context_root_path)
        session = krrez.flow.Session.by_name(session_name, context=context)
        bit = krrez.flow.bit_loader.bit_by_name(bit_name)()
        log_block = pickle.loads(picked_log_block)
        dialog_hub: krrez.flow.dialog.Hub = hallyd.ipc.client(dialog_hub_server_ipc_path)
        try:
            # noinspection PyProtectedMember
            bit._internals.prepare_apply(session, log_block, krrez.flow.dialog.HubEndpoint(dialog_hub))
            bit.__apply__()
        except Exception:
            log_block.message.fatal(traceback.format_exc())
            raise


class _ApplyTask:

    def __init__(self, bit: type["krrez.api.Bit"], log_block, process: subprocess.Popen):
        super().__init__()
        self.__bit = bit
        self.__log_block = log_block
        self.__process = process
        self.__output_pipe_thread = self.PipeReaderThread(log_block, process)
        self.__output_pipe_thread.start()

    @property
    def bit(self) -> type["krrez.api.Bit"]:
        return self.__bit

    @property
    def log_block(self):
        return self.__log_block

    @property
    def _process(self):
        return self.__process

    class PipeReaderThread(threading.Thread):

        def __init__(self, log_block, process: subprocess.Popen):
            super().__init__(daemon=True)
            self.__log_block = log_block
            self.__process = process

        def run(self):
            current_line = b""
            while True:
                buf = self.__process.stdout.read(1)
                if not buf:
                    break
                if buf == b"\n":
                    self.__log_block.message.debug(current_line.decode(errors="ignore"))
                    current_line = b""
                else:
                    current_line += buf

    @property
    def error(self) -> bool:
        return (not self.is_running) and (self.__process.returncode != 0)

    @property
    def is_running(self) -> bool:
        try:
            self.__process.wait(0)
        except subprocess.TimeoutExpired:
            return True
        self.__output_pipe_thread.join()
        return False

    def kill(self) -> None:
        self.__process.kill()

    def terminate(self) -> None:
        self.__process.send_signal(signal.SIGINT)

    def wait_terminated(self, timeout=None) -> bool:
        try:
            self.__process.wait(timeout)
        except subprocess.TimeoutExpired:
            pass
        return not self.is_running


class WasUnsuccessfulError(Exception):
    pass


class WasInterruptedError(WasUnsuccessfulError):

    def __init__(self):
        super().__init__("Was interrupted from outside.")
