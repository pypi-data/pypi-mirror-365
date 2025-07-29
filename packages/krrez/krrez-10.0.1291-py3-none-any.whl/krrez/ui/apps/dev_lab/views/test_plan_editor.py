# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.api
import krrez.coding
import krrez.flow.bit_loader
import krrez.ui.apps.dev_lab.models.test_plan_editor


class TestPlanEditor(klovve.ui.ComposedView[krrez.ui.apps.dev_lab.models.test_plan_editor.TestPlanEditor]):

    def compose(self):
        if self.model.test_plan:
            return klovve.views.Scrollable(
                item=klovve.views.Form(
                    sections=[
                        klovve.views.Label(text=self.model.bind.header_text),
                        klovve.views.Form.Section(
                            label="This test plan includes the following Tests:",
                            body=klovve.views.VerticalBox(items=[
                                klovve.views.List(
                                    items=self.model.bind.current_test_plan_tests,
                                    selected_item=self.model.bind.selected_test_name),
                                klovve.views.Button(text=self.model.bind._remove_selected_test_button_text,
                                                    is_visible=self.model.bind._remove_selected_test_button_is_visible,
                                                    action_name="remove_selected_test_from_test_plan"),
                                klovve.views.Button(text="Add a Test", action_name="add_a_test_to_test_plan")])),

                        klovve.views.Form.Section(
                            label="This Test Plan inherits from the following Test Plans:",
                            body=klovve.views.VerticalBox(items=[
                                klovve.views.List(
                                    items=self.model.bind.current_test_plan_test_plans,
                                    selected_item=self.model.bind.selected_test_plan_name),
                                klovve.views.Button(text=self.model.bind._remove_selected_test_plan_button_text,
                                                    is_visible=self.model.bind._remove_selected_test_plan_button_is_visible,
                                                    action_name="remove_selected_test_plan_from_test_plan"),
                                klovve.views.Button(text="Add a Test Plan",
                                                    action_name="add_a_test_plan_to_test_plan")])),

                        klovve.views.Form.Section(
                            label="This Test Plan uses machines for the following Test Profiles:",
                            body=klovve.views.VerticalBox(items=[
                                klovve.views.List(
                                    items=self.model.bind.current_test_plan_profiles,
                                    selected_item=self.model.bind.selected_profile_name),
                                klovve.views.Button(
                                    text=self.model.bind._remove_selected_test_profile_button_text,
                                    is_visible=self.model.bind._remove_selected_test_profile_button_is_visible,
                                    action_name="remove_selected_profile_from_test_plan"),
                                klovve.views.Button(text="Add a Test Profile",
                                                    action_name="add_a_test_profile_to_test_plan")])),

                        klovve.views.Form.Section(
                            label="If you want to make any changes to this Test Plan, modify its code in this file:",
                            body=klovve.views.Label(text=str(krrez.flow.bit_loader.bit_module_path(self.model.test_plan)))),
                        klovve.views.Form.Section(
                            body=klovve.views.Button(text="Remove this Test Plan", action_name="remove_test_plan"))]))

    @klovve.event.action("remove_test_plan")
    async def __handle_remove_test_plan(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to delete the Test Plan {self.model.current_test_plan_short_name!r}?"),
                view_anchor=event.triggering_view):
            self.model.handle_remove_test_plan(self.model.test_plan)

    @klovve.event.action("add_a_test_to_test_plan")
    async def __handle_add_a_test_to_test_plan(self, event):
        if test := await self.application.dialog(klovve.views.interact.Message(
                message=f"Please pick the Test you want to add.",
                choices=self.model.all_test_names),
                view_anchor=event.triggering_view):
            self.model.handle_add_test_to_test_plan(test, self.model.test_plan)

    @klovve.event.action("remove_selected_test_from_test_plan")
    async def __handle_remove_selected_test_from_test_plan(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to remove the Test {self.model.selected_test_name!r}"
                        f" from Test Plan {self.model.current_test_plan_short_name!r}?"),
                view_anchor=event.triggering_view):
            self.model.handle_remove_test_from_test_plan(self.model.selected_test_name, self.model.test_plan)

    @klovve.event.action("add_a_test_plan_to_test_plan")
    async def __handle_add_a_test_plan_to_test_plan(self, event):
        if test_plan := await self.application.dialog(klovve.views.interact.Message(
                message=f"Please pick the Test Plan you want to add.",
                choices=self.model.all_test_plan_names),
                view_anchor=event.triggering_view):
            self.model.handle_add_test_plan_to_test_plan(test_plan, self.model.test_plan)

    @klovve.event.action("remove_selected_test_plan_from_test_plan")
    async def __handle_remove_selected_test_plan_from_test_plan(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to remove the Test Plan {self.model.selected_test_plan_name!r}"
                        f" from Test Plan {self.model.current_test_plan_short_name!r}?"),
                view_anchor=event.triggering_view):
            self.model.handle_remove_test_plan_from_test_plan(self.model.selected_test_plan_name, self.model.test_plan)

    @klovve.event.action("add_a_test_profile_to_test_plan")
    async def __handle_add_a_test_profile_to_test_plan(self, event):
        if profile := await self.application.dialog(klovve.views.interact.Message(
                message=f"Please pick the Profile you want to add.",
                choices=self.model.all_profile_test_names),
                view_anchor=event.triggering_view):
            self.model.handle_add_test_profile_to_test_plan(profile, self.model.test_plan)

    @klovve.event.action("remove_selected_profile_from_test_plan")
    async def __handle_remove_selected_profile_from_test_plan(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to remove the Profile {self.model.selected_profile_name!r}"
                        f" from Test Plan {self.model.current_test_plan_short_name!r}?"),
                view_anchor=event.triggering_view):
            self.model.handle_remove_profile_from_test_plan(self.model.selected_profile_name, self.model.test_plan)

    def __refresh(self):
        test_plan = self.test_plan
        self.test_plan = None
        self.test_plan = test_plan
