# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import builtins

import hallyd
import klovve.variable

import krrez.coding
import krrez.flow.watch
import krrez.ui.apps.testing.views.new_test_run
import krrez.ui.apps.testing.models.new_test_run
import krrez.ui.models.list_panel
import krrez.ui.views.list_panel
import krrez.ui.models.session
import krrez.ui.views.session
import krrez.testing.landmark
import krrez.ui.apps.testing.models.main


class Main(klovve.ui.ComposedView[krrez.ui.apps.testing.models.main.Main]):

    def _(self):
        if not self.model:
            return None
        if self.model.selected_session:
            return krrez.ui.views.session.Session(
                model=krrez.ui.models.session.Session(
                    session=self.model.selected_session,
                    actions=[
                        klovve.views.Button(
                            text="Abort",
                            action_name="abort",
                            is_visible=self.model.bind.selected_session_can_be_aborted),
                        klovve.views.Button(
                            text="Landmark",
                            action_name="landmark_menu",
                            is_visible=self.model.bind.selected_session_has_landmark)]))
        return krrez.ui.apps.testing.views.new_test_run.NewTestRun(
            model=krrez.ui.apps.testing.models.new_test_run.NewTestRun(
                all_test_plans=self.model.bind.all_test_plans,
                selected_test_plan=self.model.bind.selected_test_plan))
    panel_body = klovve.ui.computed_property(_)

    @klovve.event.event_handler(krrez.ui.apps.testing.views.new_test_run.StartTestEvent)
    def __handle_start_test_plan(self, event: krrez.ui.apps.testing.views.new_test_run.StartTestEvent) -> None:
        event.stop_processing()
        self.model.handle_start_test_plan()

    def compose(self):
        return krrez.ui.views.list_panel.ListPanel(
            model=krrez.ui.models.list_panel.ListPanel(
                is_list_visible=self.model.bind.is_session_list_visible,
                items=self.model.bind.all_sessions,
                item_label_func=lambda item: item.name if item else "New test run",
                selected_items=self.model.bind.selected_session__as_list,
                body=self.bind.panel_body))

    @klovve.event.action("abort")
    async def __handle_abort_requested(self, event: klovve.app.Application.ActionTriggeredEvent):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message="Do you really want to abort this test run?"),
                view_anchor=event.triggering_view):
            self.model.handle_abort_requested()

    @klovve.event.action("landmark_menu")
    async def __handle_landmark_menu_requested(self, event: klovve.app.Application.ActionTriggeredEvent):
        landmark_size_str = hallyd.fs.byte_size_to_human_readable(self.model.selected_session_landmark_size)

        action = await self.application.dialog(klovve.views.interact.Message(
            message=f"This test run has been stopped immaturely, e.g. due to a system shutdown.\n\n"
                    f"There is a landmark (taking {landmark_size_str}) that you can resume from.\n\n"
                    f"Please choose what you want to do with this landmark.",
            choices=(("Resume from here", 0), ("Delete", 1))),
            view_anchor=event.triggering_view,
            is_closable_by_user=True)

        if action == 0:
            reader = krrez.testing.landmark.start_resume_tests_from_landmark(self.model.selected_session)
            self.model._refresh_sessions()  # TODO
            new_session_ = [s for s in self.model.all_sessions if s and s.name == reader.session.name]
            if new_session_:
                self.model.selected_session__as_list = (new_session_[0],)

        elif action == 1:
            if await self.application.dialog(
                    klovve.views.interact.MessageYesNo(message="Do you really want to remove this landmark?"),
                    view_anchor=event.triggering_view):
                self.model.handle_forget_landmark()
