#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
The Krrez CLI.
"""
import abc
import argparse
import contextlib
import json
import logging
import os
import sys
import threading
import time
import traceback
import typing as t

try:  # weird, but useful in some cases ;)
    if "__main__" == __name__:
        import krrez.api
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.realpath(__file__)+"/../.."))

import hallyd
import klovve

import krrez.asset
import krrez.coding
import krrez.flow.bit_loader
import krrez.flow.ui
import krrez.flow.logging
import krrez.flow.runner
import krrez.flow.watch
import krrez.seeding.profile_loader
import krrez.testing.landmark


_logger = logging.getLogger("krrez.krrez_cli")


def main() -> None:
    if os.environ.get("KRREZ_DEBUG_LOG", "") == "1":
        logging.basicConfig(level=logging.DEBUG)
    hallyd.cleanup.cleanup_after_exit()
    arg_parser = parser(only_relevant=True, only_documentation=False)
    args = arg_parser.parse_args().__dict__
    command_name = (args.pop("command") or "studio").replace("-", "_")
    command_type = getattr(Commands, f"Command_{command_name}")
    command = command_type(args.pop("context_path"))
    _janitor(command.context)

    try:
        command(**args)
    except Exception as ex:
        _logger.debug(traceback.format_exc())
        print(f"Error: {ex}", file=sys.stderr)
        sys.exit(1)


# noinspection PyUnusedLocal
def parser(*, only_relevant: bool = False, only_documentation: bool = True) -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        description=None if only_documentation
        else f"Welcome to Krrez {krrez.asset.project_info.version}! For more information, read"
             f" {'file://'+str(krrez.asset.data.readme_pdf('en'))!r} and visit"
             f" {krrez.asset.project_info.homepage_url!r}.")
    arg_parser.add_argument("--context-path", help=argparse.SUPPRESS)
    p_cmd = arg_parser.add_subparsers(help="What to do?", required=False, dest="command", metavar="[command]")

    if (not only_relevant) or krrez.flow.is_krrez_machine():
        p_cmd_bits = p_cmd.add_parser("bits", help="Manage Krrez bits.")
        p_cmd_bits_cmd = p_cmd_bits.add_subparsers(help="What to do with bits?", required=True, dest="subcommand",
                                                   metavar="[subcommand]")
        p_cmd_bits_cmd_list = p_cmd_bits_cmd.add_parser("list", help="List all bits.")
        p_cmd_bits_cmd_info = p_cmd_bits_cmd.add_parser("info", help="Show information for some bits.")
        p_cmd_bits_cmd_info.add_argument("bits", type=str, help="The bits to show.", nargs="*")

        p_cmd_logs = p_cmd.add_parser("logs", help="Read logs.")
        p_cmd_logs_cmd = p_cmd_logs.add_subparsers(help="What to do with logs?", required=False, dest="subcommand",
                                                   metavar="[subcommand]")
        p_cmd_logs_cmd_list = p_cmd_logs_cmd.add_parser("list", help="List all existing sessions.")
        p_cmd_logs_cmd_show = p_cmd_logs_cmd.add_parser("show", help="Show the log for a particular session.")
        p_cmd_logs_cmd_show.add_argument("session", type=str, help="The session to show.")
        p_cmd_logs_cmd_show.add_argument("--verbose", help="Show debug output as well.", action="store_true")

    p_cmd_seeding = p_cmd.add_parser("seeding", help="Seed Krrez to a machine.")
    p_cmd_seeding_cmd = p_cmd_seeding.add_subparsers(help="What to do with seeding?", required=False, dest="subcommand",
                                                     metavar="[subcommand]")
    p_cmd_seeding_cmd_sow = p_cmd_seeding_cmd.add_parser("sow", help="Sow a seed. This will purge all existing data on"
                                                                     " the target device!")
    p_cmd_seeding_cmd_sow.add_argument("profile", type=str, help="Seed profile.")
    p_cmd_seeding_cmd_sow.add_argument("arguments", type=str, help="Arguments for this profile, as json string.")
    p_cmd_seeding_cmd_sow.add_argument("target_device", type=str, help="Path to target device.")
    p_cmd_seeding_cmd_profiles = p_cmd_seeding_cmd.add_parser("profiles", help="Manage profiles.")
    p_cmd_seeding_cmd_profiles_cmd = p_cmd_seeding_cmd_profiles.add_subparsers(help="What to do with profiles?",
                                                                               dest="subsubcommand", required=True,
                                                                               metavar="<subsubcommand>")
    p_cmd_seeding_cmd_profiles_cmd_list = p_cmd_seeding_cmd_profiles_cmd.add_parser(
        "list", help="List all available profiles.")
    p_cmd_seeding_cmd_profiles_cmd_info = p_cmd_seeding_cmd_profiles_cmd.add_parser(
        "info", help="Show further details for a profile.")
    p_cmd_seeding_cmd_profiles_cmd_info.add_argument("profile", type=str, help="The profile to show.")

    p_cmd_dev_lab = p_cmd.add_parser("dev-lab", help="Krrez development tool.")

    p_cmd_testing = p_cmd.add_parser("testing", help="Krrez testing.")
    p_cmd_testing_cmd = p_cmd_testing.add_subparsers(help="What to do with testing?", required=False, dest="subcommand",
                                                     metavar="[subcommand]")
    p_cmd_testing_cmd_run = p_cmd_testing_cmd.add_parser("run", help="Run a test plan.")
    p_cmd_testing_cmd_run.add_argument("plan", type=str, help="Test plan name.")
    p_cmd_testing_cmd_plans = p_cmd_testing_cmd.add_parser("plans", help="Manage test plans.")
    p_cmd_testing_cmd_plans_cmd = p_cmd_testing_cmd_plans.add_subparsers(help="What to do with test plans?",
                                                                       dest="subsubcommand", required=True,
                                                                       metavar="<subsubcommand>")
    p_cmd_testing_cmd_run_plans_cmd_list = p_cmd_testing_cmd_plans_cmd.add_parser(
        "list", help="List all available test plans.")
    p_cmd_testing_cmd_logs = p_cmd_testing_cmd.add_parser("logs", help="Manage test logs.")
    p_cmd_testing_cmd_logs_cmd = p_cmd_testing_cmd_logs.add_subparsers(help="What to do with test logs?",
                                                                       dest="subsubcommand", required=True,
                                                                       metavar="<subsubcommand>")
    p_cmd_testing_cmd_logs_cmd_list = p_cmd_testing_cmd_logs_cmd.add_parser(
        "list", help="List all existing test sessions.")
    p_cmd_testing_cmd_logs_cmd_show = p_cmd_testing_cmd_logs_cmd.add_parser("show", help="Show the log for a particular"
                                                                                         " test session.")
    p_cmd_testing_cmd_logs_cmd_show.add_argument("session", type=str, help="The session to show.")
    p_cmd_testing_cmd_logs_cmd_show.add_argument("--verbose", help="Show debug output as well.", action="store_true")
    p_cmd_testing_cmd_landmarks = p_cmd_testing_cmd.add_parser("landmarks", help="Manage test landmarks.")
    p_cmd_testing_cmd_landmarks_cmd = p_cmd_testing_cmd_landmarks.add_subparsers(help="What to do with test landmarks?",
                                                                                 dest="subsubcommand", required=True,
                                                                                 metavar="<subsubcommand>")
    p_cmd_testing_cmd_run_landmarks_cmd_list = p_cmd_testing_cmd_landmarks_cmd.add_parser(
        "list", help="List all available test landmarks.")
    p_cmd_testing_cmd_run_landmarks_cmd_resume = p_cmd_testing_cmd_landmarks_cmd.add_parser(
        "resume", help="Resume a test landmark.")
    p_cmd_testing_cmd_run_landmarks_cmd_resume.add_argument("session", type=str, help="The session to resume.")
    p_cmd_testing_cmd_run_landmarks_cmd_remove = p_cmd_testing_cmd_landmarks_cmd.add_parser(
        "remove", help="Remove a test landmark.")
    p_cmd_testing_cmd_run_landmarks_cmd_remove.add_argument("session", type=str, help="The session to remove the"
                                                                                      " landmark for.")

    return arg_parser


class _Command(abc.ABC):

    def __init__(self, context_path):
        self.__context = krrez.flow.Context(hallyd.fs.Path(context_path) if context_path else None)

    @property
    def context(self):
        return self.__context

    @contextlib.contextmanager
    def ui_app(self, app_name: str, *, unavailable_message: t.Optional[str] = None, **kwargs):
        unavailable_message = unavailable_message or ("This command is not available in an interactive way on your"
                                                      " system.")
        try:
            with krrez.flow.ui.app(app_name, self.context.path, **kwargs) as (app, app_ctrl):
                yield app, app_ctrl
        except klovve.driver.Driver.IncompatibleError as ex:
            raise Commands.AppUnavailableError(f"{unavailable_message} Please add '--help' to your command line and"
                                               f" use one of the listed sub-commands instead.") from ex

    def __getattr__(self, item):
        if item.startswith("sub_"):
            item = item[4:]
            command_name = f"Command_{item}"
            if hasattr(self, command_name):
                subcommand_type = getattr(self, command_name, None)
                subcommand = subcommand_type(context_path=self.context.path)
                def foo(**kwargs):
                    kwwargs = {}
                    for k, v in kwargs.items():
                        if k.endswith("subcommand"):
                            k = k[3:]
                        kwwargs[k] = v
                    return subcommand(**kwwargs)
                return foo
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def __call__(self, *, subcommand: t.Optional[str] = None, **kwargs):
        if subcommand:
            subcommand_fct = getattr(self, f"sub_{subcommand}", None)
            if not subcommand_fct:
                raise RuntimeError(f"the command '{subcommand}' is not valid")
            return subcommand_fct(**kwargs)
        self.main()

    def main(self):
        pass


class Commands:

    class AppUnavailableError(RuntimeError):
        pass

    # noinspection PyPep8Naming
    class Command_bits(_Command):

        def sub_list(self) -> None:
            for bit in krrez.flow.bit_loader.all_normal_bits():
                print(krrez.flow.bit_loader.bit_name(bit))

        def sub_info(self, *, bits: list[str]) -> None:
            for bit_name in bits:
                try:
                    bit = krrez.flow.bit_loader.bit_by_name(bit_name)()
                    print(f"{bit_name}: {'' if self.context.is_bit_installed(bit) else 'not '}installed")
                except krrez.flow.bit_loader.BitNotFoundError:
                    print(f"{bit_name}: not found")

    # noinspection PyPep8Naming
    class Command_logs(_Command):

        def main(self) -> None:
            with self.ui_app("log_browser") as (app, app_ctrl):
                app_ctrl.run()

        def sub_list(self) -> None:
            _list_sessions(self.context.get_sessions())

        def sub_show(self, *, session: str, verbose: bool) -> None:
            _dump_session(session, verbose, self.context)

    # noinspection PyPep8Naming
    class Command_seeding(_Command):

        # noinspection PyPep8Naming
        class Command_profiles(_Command):

            def sub_list(self) -> None:
                for profile in krrez.seeding.profile_loader.browsable_profiles():
                    print(profile.name)

            def sub_info(self, profile: str) -> None:
                for profile_ in krrez.seeding.profile_loader.all_profiles():
                    if profile_.name == profile:
                        print("Parameters:")
                        for open_parameter in profile_.open_parameters:
                            print(f" {open_parameter.name}\n  (type: {open_parameter.type})")
                        print("Possible target devices (insert your empty medium in order to show it here):")
                        for target_device, target_device_description in profile_.available_target_devices:
                            print(f" {target_device}\n  ({target_device_description})")
                        break
                else:
                    raise RuntimeError(f"profile does not exist: {profile}")

        def main(self) -> None:
            with self.ui_app("seeding") as (app, app_ctrl):
                app_ctrl.run()

        def sub_sow(self, *, profile: str, arguments: str, target_device: str) -> None:
            with self.ui_app("seeding", start_with=(profile, target_device, json.loads(arguments))) as (app, app_ctrl):
                app_ctrl.run()

    # noinspection PyPep8Naming
    class Command_dev_lab(_Command):

        def main(self) -> None:
            with self.ui_app("dev_lab") as (app, app_ctrl):
                app_ctrl.run()

    # noinspection PyPep8Naming
    class Command_testing(_Command):

        # noinspection PyPep8Naming
        class Command_plans(_Command):

            def sub_list(self) -> None:
                for test_plan_name in krrez.testing.all_available_test_plans():
                    print(test_plan_name)

        # noinspection PyPep8Naming
        class Command_logs(_Command):

            def sub_list(self) -> None:
                _list_sessions(krrez.testing.all_test_sessions(self.context))

            def sub_show(self, *, session: str, verbose: bool) -> None:
                for session_ in krrez.testing.all_test_sessions(self.context):
                    if session_.name == session:
                        _dump_session(session, verbose, session_.context)
                        break
                else:
                    raise RuntimeError(f"test session does not exist: {session}")

        # noinspection PyPep8Naming
        class Command_landmarks(_Command):

            def sub_list(self) -> None:
                for session in krrez.testing.all_test_sessions(self.context):
                    if krrez.testing.landmark.has_resumable_landmark(session):
                        print(session.name)

            def sub_resume(self, *, session: str) -> None:
                session_path = list(self.context.path.glob(f"testing/sub/*/runs/{session}"))[0]
                context_path = session_path.parent.parent
                context = krrez.flow.Context(context_path)
                session_ = krrez.testing.landmark.start_resume_tests_from_landmark(krrez.flow._Session(context,
                                                                                                       session)).session
                with self.ui_app("testing", start_with_session=session_) as (app, app_ctrl):
                    app_ctrl.run()

            def sub_remove(self, *, session: str) -> None:
                for session_ in krrez.testing.all_test_sessions(self.context):
                    if session_.name == session:
                        krrez.testing.landmark.forget_landmark(session_)
                        break
                else:
                    raise RuntimeError(f"test session does not exist: {session}")

        def main(self) -> None:
            with self.ui_app("testing") as (app, app_ctrl):
                app_ctrl.run()

        def sub_run(self, *, plan: str) -> None:
            session = krrez.testing.start_tests([
                krrez.coding.TestPlans.test_plan_name_to_bit_name(plan)], context=self.context).session
            with self.ui_app("testing", start_with_session=session) as (app, app_ctrl):
                app_ctrl.run()

    # noinspection PyPep8Naming
    class Command_studio(_Command):

        def main(self) -> None:
            with self.ui_app("studio", unavailable_message="You are trying to open the Krrez main user interface,"
                                                           " but it cannot be used on your system.") as (app, app_ctrl):
                app_ctrl.run()


def _list_sessions(sessions: t.Iterable["krrez.flow.Session"]) -> None:
    for session in sessions:
        print(session.name)


def _dump_session(session_name: str, verbose: bool, context: "krrez.flow.Context") -> None:
    for session_ in context.get_sessions():
        if session_.name == session_name:
            _dump_session__dump(session_, verbose)
            break
    else:
        raise RuntimeError(f"session does not exist: {session_name}")


def _dump_session__dump(session: "krrez.flow.Session", verbose: bool) -> None:

    root_block = [None, None, None, False, []]
    blocks = {"": root_block}

    def log_block_arrived(parent_block_id, block_id, message, began_at, only_single_time, severity):
        if not block_id:
            return
        if (verbose or severity >= krrez.flow.logging.Severity.INFO) and (parent_block := blocks.get(parent_block_id)):
            blocks[block_id] = new_block = [message, began_at, None, only_single_time, []]
            parent_block[4].append(new_block)

    def log_block_changed(block_id, ended_at):
        if block := blocks.get(block_id):
            block[2] = ended_at

    def print_block(block, indent: int = 0):
        if block[0] is not None:
            print((indent*" ") + (block[1].strftime("%X") + "  ").ljust(12)
                  + ("" if block[3] else ((block[2].strftime("%X")) if block[2] else ". . . . .")).ljust(12)
                  + "  " + block[0])
        for child_block in block[4]:
            print_block(child_block, indent + 2)

    with krrez.flow.watch.Watch(session, log_block_arrived_handler=log_block_arrived,
                                log_block_changed_handler=log_block_changed) as watch:
        time.sleep(3)  # TODO shitty hack
        print(watch.state_text)

    print_block(root_block)


def _janitor(context: "krrez.flow.Context") -> None:
    def run():
        try:
            krrez.testing.clean_up_old_test_sessions(context)
            time.sleep(1)
            krrez.testing.landmark.clean_up_old_landmarks(context)
        except Exception:
            _logger.debug(traceback.format_exc())

    threading.Thread(target=run).start()


if __name__ == "__main__":
    main()

# TODO the process (at least UIs when we run tests) doesn't always terminate
