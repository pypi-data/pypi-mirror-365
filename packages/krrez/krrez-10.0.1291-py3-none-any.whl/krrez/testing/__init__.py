# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Krrez testing.
"""
import datetime
import typing as t

import hallyd.fs

import krrez.coding
import krrez.flow.bit_loader
import krrez.flow.runner
import krrez.flow.watch


def start_tests(bit_names: t.Iterable[str], *,
                context: t.Optional[krrez.flow.Context] = None) -> krrez.flow.watch.Watch:
    """
    Start a test run.

    :param bit_names: The test Bit names to apply. Those Bits are usually test plans. See
                      :py:func:`all_available_test_plans`. There is usually just one.
    :param context: The context. Note: The actual test run will happen in a sub-context of it.
    """
    return _TestingEngine().start(context=krrez.flow.create_blank_context(_testing_context(context)),
                                  bit_names=bit_names)


def all_available_test_plans() -> list[str]:
    """
    The available test plans.

    You usually call :py:func:`all_available_test_plans` with one of them.
    """
    result = []

    for bit in krrez.flow.bit_loader.all_bits():
        bit_name = krrez.flow.bit_loader.bit_name(bit)
        if krrez.coding.TestPlans.is_bit_name_for_test_plan(bit_name):
            result.append(krrez.coding.TestPlans.bit_name_to_test_plan_name(bit_name))

    return sorted(result)


def all_test_sessions(context: t.Optional[krrez.flow.Context] = None) -> list[krrez.flow.Session]:
    """
    All test sessions from the past.

    :param context: The context.
    """
    result = []
    for test_run_context in _testing_context(context).get_blank_contexts():
        result += test_run_context.get_sessions()
    return sorted(result, key=lambda session: session.name)


def test_plan_for_test_session(session: krrez.flow.Session) -> str:
    # TODO ugly
    chosen_bits = [s for s in session.path("chosen_bits").read_text().split("\n") if s]
    if len(chosen_bits) != 1 or not chosen_bits[0].startswith("zz_test.zz_plans."):
        raise RuntimeError("not a valid test session")
    return chosen_bits[0][17:]


def clean_up_old_test_sessions(context: t.Optional[krrez.flow.Context] = None) -> None:
    """
    Remove old test sessions.

    :param context: The context.
    """
    is_old = False
    for i, session in enumerate(reversed(all_test_sessions(context))):
        now = datetime.datetime.now()
        is_old = is_old or (now - (krrez.flow.watch.Watch(session).ended_at or now)) > datetime.timedelta(days=7)
        if (i >= 50) or is_old:
            session.path.remove(on_error=hallyd.fs.OnRemoveError.SKIP_AND_IGNORE)  # TODO wild wild west


class _TestingEngine(krrez.flow.runner.Engine):

    _worker_pool_size = 20

    def _apply_message(self, bit_name):
        if bit_name.startswith("zz_test."):
            return f"Testing {bit_name[8:]}."
        return super()._apply_message(bit_name)

    def _do_finish(self, session, runner_writer, success):
        import krrez.testing.landmark
        krrez.testing.landmark.forget_landmark(session)
        if not success:
            runner_writer.dialog.choose("This test run failed or was aborted.\n\nYou can now do problem analysis"
                                        " on the virtual machines that ran this test.\n\nOnce you continue"
                                        " here, they will be removed.", choices=["OK"])


def _testing_context(context: t.Optional[krrez.flow.Context]) -> krrez.flow.Context:
    return krrez.flow.Context((context or krrez.flow.Context()).path("testing"))
