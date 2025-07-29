# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio

import klovve.variable

import krrez.coding
import krrez.flow.watch
import krrez.testing.landmark


class Main(klovve.model.Model):

    krrez_application: krrez.ui.Application = klovve.model.property()

    async def _(self):
        # dirty hack - otherwise it will show you the "new test" panel even if you started it with a given test plan
        for _ in range(10):
            await asyncio.sleep(0)
        if self.start_with_session:
            self._refresh_sessions()
            new_session_ = [session for session in self.all_sessions if session and session.name == self.start_with_session.name]
            if new_session_:
                self.selected_session__as_list = (new_session_[0],)
    __ = klovve.model.computed_property(_)

    all_sessions: list[krrez.flow.Session|None] = klovve.model.list_property()

    selected_session__as_list: list[krrez.flow.Session|None] = klovve.model.list_property(initial=(None,))

    all_test_plans: list[str] = klovve.model.list_property()

    selected_test_plan: str|None = klovve.model.property()

    start_with_session: krrez.flow.Session|None = klovve.model.property()

    # a special counter; the value does not matter, but it triggers refreshing for some computed properties
    _session_touched_counter: int = klovve.model.property(initial=1, is_settable=False)

    def _(self):
        str(self._session_touched_counter)

        if self.selected_session:
            try:
                if krrez.testing.landmark.has_resumable_landmark(self.selected_session):
                    return krrez.testing.landmark.landmark_size_on_disk(self.selected_session)
            except IOError:
                pass
    selected_session_landmark_size: int|None = klovve.model.computed_property(_)

    def _(self):
        str(self._session_touched_counter)

        if self.selected_session:
            try:
                return krrez.testing.landmark.has_resumable_landmark(self.selected_session)
            except IOError:
                pass
    selected_session_has_landmark: bool = klovve.model.computed_property(_)

    def _(self):
        str(self._session_touched_counter)

        if self.selected_session:
            return krrez.flow.watch.Watch(self.selected_session).ended_at is None
        return False
    selected_session_can_be_aborted: bool = klovve.model.computed_property(_)

    def _(self):
        if len(self.selected_session__as_list) > 0:
            return self.selected_session__as_list[0]
    selected_session: krrez.flow.Session|None = klovve.model.computed_property(_)

    def _(self):
        return not self.start_with_session
    is_session_list_visible: bool = klovve.model.computed_property(_)

    @klovve.timer.run_timed(interval=60)
    def _refresh_sessions(self):
        self.all_sessions = (None,
                             *reversed(krrez.testing.all_test_sessions(self.krrez_application.runtime_data.context)))

    @klovve.timer.run_timed(interval=2*60)
    def __refresh_available_test_plans(self):
        self.all_test_plans = krrez.testing.all_available_test_plans()

    @klovve.timer.run_timed(interval=60)
    def __refresh_landmark_foo(self):
        self.__session_touched()

    def handle_start_test_plan(self):
        watch = krrez.testing.start_tests([krrez.coding.TestPlans.test_plan_name_to_bit_name(self.selected_test_plan)],
                                          context=self.krrez_application.runtime_data.context)
        self._refresh_sessions()
        new_session_ = [session for session in self.all_sessions if session and session.name == watch.session.name]
        if new_session_:
            self.selected_session__as_list = (new_session_[0],)

    def handle_abort_requested(self):
        krrez.flow.watch.Watch(self.selected_session).abort()
        self.__session_touched()

    def handle_forget_landmark(self):
        krrez.testing.landmark.forget_landmark(self.selected_session)
        self.__session_touched()

    def __session_touched(self):
        self._introspect.set_property_value(Main._session_touched_counter, self._session_touched_counter + 1)
