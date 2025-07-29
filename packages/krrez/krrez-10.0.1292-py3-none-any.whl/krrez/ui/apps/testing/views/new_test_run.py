# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui.apps.testing.models.new_test_run


class NewTestRun(klovve.ui.ComposedView[krrez.ui.apps.testing.models.new_test_run.NewTestRun]):

    def compose(self):
        return klovve.views.Scrollable(
            body=klovve.views.Form(
                sections=[
                    klovve.views.Label(text="Start a new test run."),
                    klovve.views.Form.Section(
                        label="Please choose the test to run.",
                        body=klovve.views.DropDown(
                            items=self.model.bind.all_test_plans,
                            selected_item=self.model.bind.selected_test_plan)),
                    klovve.views.Form.Section(
                        body=klovve.views.Button(
                            text="Start test",
                            action_name="start_test",
                            is_enabled=self.model.bind.is_form_valid))],
                horizontal_layout=klovve.ui.Layout(klovve.ui.Align.CENTER),
                vertical_layout=klovve.ui.Layout(klovve.ui.Align.CENTER)))

    @klovve.event.action("start_test")
    def __start_test(self, event):
        event.stop_processing()
        self.trigger_event(StartTestEvent())


class StartTestEvent(klovve.event.Event):
    pass
