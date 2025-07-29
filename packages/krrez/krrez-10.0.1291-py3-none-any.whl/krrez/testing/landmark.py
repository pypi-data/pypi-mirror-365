# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Platform level support for landmarks in testing.
"""
import datetime
import json
import shutil
import typing as t

import hallyd

import krrez.asset
import krrez.bits.zz_test.zz_run
import krrez.flow.bit_loader
import krrez.flow.runner
import krrez.flow.watch
import krrez.testing.api


def set_landmark(run: "krrez.bits.zz_test.zz_run.Bit",
                 after_reboot: "krrez.testing.api.AfterRebootHandler", name: str) -> None:
    """
    Set a landmark.

    :py:func:`start_resume_tests_from_landmark` can resume a terminated session from the past from the current
    situation. Note that all machines will shutdown during that time, and that no other Bits may execute in parallel.

    :param run: The run Bit.
    :param after_reboot: The after reboot handler.
    :param name: The landmark name.
    """
    # TODO check if this is the only running bit atm
    if run.data("last_landmark") != name:
        all_machines = run.all_machines
        session = run._internals.session
        session_last_landmark_path = _last_landmark_path(session)
        running_machines = [machine for machine in all_machines if not machine.is_shut_down]

        run.set_data("last_landmark", name)
        #with krrezzeedtest.log.InfoBlock("Arrived at a landmark. Shutting down machines for a snapshot."):
        run.set_data("running_machines", [machine.short_name for machine in running_machines])

        hallyd.lang.execute_in_parallel([machine.shut_down for machine in running_machines])  # TODO machine.shut_down() does not work great for (graphical) workstations?

        for machine in all_machines:
            if not machine.is_shut_down:
                raise RuntimeError(f"landmarks can only be set when all machines are shut down, but"
                                   f" {machine.short_name} is not")

        free_space = shutil.disk_usage(session.path).free
        try:
            old_landmark_size = hallyd.fs.disk_usage(session.path("landmark"))
        except IOError:
            old_landmark_size = 0

        if free_space < 3 * old_landmark_size:
            session_last_landmark_path.remove(on_error=hallyd.fs.OnRemoveError.SKIP_AND_IGNORE)

        temp_target_dir = _base_landmark_path(session)("_tmp")
        temp_target_dir.remove(not_exist_ok=True).make_dir(until=hallyd.fs.Path("/TODO/.."), readable_by_all=True)
        run._run_dir.copy_to(temp_target_dir("run"), sparse=True, readable_by_all=True)
        temp_target_dir("data").set_data(hallyd.bindle.dumps({
            "name": run._internals.origin_bit.name,
            "domains": [machine._serialized_dom() for machine in all_machines]}))
        session_last_landmark_path.remove(on_error=hallyd.fs.OnRemoveError.SKIP_AND_IGNORE)
        temp_target_dir.rename(session_last_landmark_path)

    #with krrezzeedtest.log.InfoBlock(f"Starting machines for continuing."):
    boot_machines = [run.machine(machine_name) for machine_name in run.data("running_machines")]
    hallyd.lang.execute_in_parallel([_Boot(machine, after_reboot) for machine in boot_machines])


def forget_landmark(session: krrez.flow.Session) -> None:
    """
    Remove landmark information for a session.

    :param session: The session to clean.
    """
    _base_landmark_path(session).remove(on_error=hallyd.fs.OnRemoveError.SKIP_AND_IGNORE)


def clean_up_old_landmarks(context: t.Optional[krrez.flow.Context] = None):
    """
    Remove old landmarks.

    :param context: The context.
    """
    MAX_COUNT = 2

    sessions = []
    for session in krrez.testing.all_test_sessions(context):
        session_ended_at = krrez.flow.watch.Watch(session).ended_at
        if session_ended_at:
            if (datetime.datetime.now() - session_ended_at) > datetime.timedelta(days=14):
                forget_landmark(session)
            else:
                sessions.append(session)

    sessions_with_landmarks = [s for s in reversed(sessions) if has_resumable_landmark(s)]

    test_plans_by_session = {s: krrez.testing.test_plan_for_test_session(s) for s in sessions_with_landmarks}

    test_plans = [test_plans_by_session[s] for s in sessions_with_landmarks]
    for i, test_plan in reversed(list(enumerate(test_plans))):
        if len(sessions_with_landmarks) <= MAX_COUNT:
            break
        if test_plan in test_plans[:i]:
            test_plans.pop(i)
            forget_landmark(sessions_with_landmarks.pop(i))

    for session in sessions_with_landmarks[MAX_COUNT:]:
        forget_landmark(session)


def has_resumable_landmark(session: krrez.flow.Session) -> bool:
    """
    Return whether a session can be resumed from a landmark.

    :param session: The session to check.
    """
    if not _last_data_landmark_path(session).exists():
        return False
    return krrez.flow.watch.Watch(session).ended_at is not None


def landmark_size_on_disk(session: krrez.flow.Session) -> int:
    """
    Return the disk usage of landmark data for a session (in bytes).

    :param session: The session to check.
    """
    return hallyd.fs.disk_usage(_base_landmark_path(session))


def landmark_name_for_session(session: krrez.flow.Session) -> t.Optional[str]:
    """
    Return the landmark name for a session (or :code:`None` if there is no landmark data for this session).

    :param session: The session to check.
    """
    if has_resumable_landmark(session):
        with open(_last_data_landmark_path(session), "r") as f:
            return json.load(f)["name"]


def start_resume_tests_from_landmark(session: krrez.flow.Session) -> krrez.flow.watch.Watch:
    """
    Start a test run that resumes a session from the past from its last landmark.

    :param session: The session to resume.
    """
    landmark_name = landmark_name_for_session(session)
    testing_context = session.context.parent_context
    test_run_context = krrez.flow.create_blank_context(testing_context)
    landmark_dir_path = session.path("landmark")
    last_landmark_dir_path = landmark_dir_path("last")

    if not has_resumable_landmark(session):
        raise RuntimeError(f"the session '{session}' cannot be resumed")

    last_landmark = json.loads(last_landmark_dir_path("data").read_text())
    engine = _LandmarkResumingTestingEngine(landmark_name, last_landmark_dir_path("run"), last_landmark["domains"])
    return engine.start(context=test_run_context, bit_names=krrez.flow.watch.Watch(session).chosen_bits)


class _LandmarkResumingTestingEngine(krrez.testing._TestingEngine):

    def __init__(self, landmark_name, run_dir, xml_domains):
        super().__init__()
        self.__landmark_name = landmark_name
        self.__run_dir = run_dir
        self.__xml_domains = xml_domains

    def _do_prepare(self, session, install_bits):
        run = krrez.asset.bit(krrez.bits.zz_test.zz_run.Bit, skip_installed_check=True)
        run._internals.prepare_apply(session, None, None)

        if self.__run_dir and self.__run_dir.exists():  # TODO it would fail otherwise anyways, right?
            run._apply(create=False)
            session.path("run").remove(on_error=hallyd.fs.OnRemoveError.SKIP_AND_IGNORE)
            self.__run_dir.copy_to(session.path("run"), sparse=True, readable_by_all=True)

            # TODO odd
            for share_dir in session.path("run/machines").glob("*/share"):
                share_dir.change_access(0o777, recursive=True)

        if self.__xml_domains:
            for xml_domain in self.__xml_domains:
                # noinspection PyProtectedMember
                run._deserialize_dom(xml_domain)

        return super()._do_prepare(session, install_bits)

    def _do_install_bit(self, bit, log_block, session, runner_writer):
        if self.__landmark_name:
            if krrez.flow.bit_loader.bit_name(bit) == self.__landmark_name:
                self.__landmark_name = None
            else:
                return krrez.flow.runner._ApplyTask(
                    bit, log_block,
                    super()._do_install_bit(krrez.flow.bit_loader.bit_by_name("noop.SPECIAL.Bit")(),
                                            log_block, session, runner_writer)._process)

        return super()._do_install_bit(bit, log_block, session, runner_writer)


def _base_landmark_path(session: krrez.flow.Session) -> hallyd.fs.Path:
    return session.path("landmark")


def _last_landmark_path(session: krrez.flow.Session) -> hallyd.fs.Path:
    return _base_landmark_path(session)("last")


def _last_data_landmark_path(session: krrez.flow.Session) -> hallyd.fs.Path:
    return _last_landmark_path(session)("data")


class _Boot:

    def __init__(self, machine: "krrez.bits.zz_test.zz_run.Machine",
                 after_reboot: "krrez.testing.api.AfterRebootHandler"):
        self.__machine = machine
        self.__after_reboot = after_reboot

    def __call__(self):
        self.__machine.turn_on()
        self.__after_reboot.after_reboot(self.__machine.short_name)
