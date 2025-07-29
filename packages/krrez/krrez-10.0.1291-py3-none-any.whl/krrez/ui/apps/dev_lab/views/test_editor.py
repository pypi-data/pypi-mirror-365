# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.api
import krrez.coding
import krrez.flow.bit_loader
import krrez.ui.apps.dev_lab.models.test_editor


class TestEditor(klovve.ui.ComposedView[krrez.ui.apps.dev_lab.models.test_editor.TestEditor]):

    def compose(self):
        if self.model.test:
            return klovve.views.Scrollable(
                item=klovve.views.Form(
                    items=[
                        klovve.views.Label(text=self.model.bind.header_text),
                        klovve.views.Form.Section(
                            label="This Test is associated to the following Profiles:",
                            body=klovve.views.VerticalBox(
                                items=[
                                    klovve.views.List(
                                        items=self.model.bind.current_test_profiles,
                                        selected_item=self.model.bind.selected_profile_name),
                                    klovve.views.Button(text=self.model.bind._remove_selected_profile_button_text,
                                                        is_visible=self.model.bind._remove_selected_profile_button_is_visible,
                                                        action_name="remove_selected_profile_from_test"),
                                    klovve.views.Button(text="Add a Profile", action_name="add_a_profile_to_test")])),
                        klovve.views.Form.Section(
                            label="If you want to make any changes to this Test, modify its code in this file:",
                            body=klovve.views.Label(text=str(krrez.flow.bit_loader.bit_module_path(self.model.test)))),
                        klovve.views.Form.Section(
                            body=klovve.views.Button(text="Remove this Test", action_name="remove_test"))]))

    @klovve.event.action("remove_test")
    async def __handle_remove_test(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to delete the Test {self.model.current_test_short_name!r}?"),
                view_anchor=event.triggering_view):
            self.model.handle_remove_test(self.model.test)

    @klovve.event.action("add_a_profile_to_test")
    async def __handle_add_a_profile_to_test(self, event):
        if profile := await self.application.dialog(klovve.views.interact.Message(
                message=f"Please pick the Profile you want to add.",
                choices=self.model.all_profile_test_names),
                view_anchor=event.triggering_view):
            self.model.handle_add_profile_to_test(profile, self.model.test)

    @klovve.event.action("remove_selected_profile_from_test")
    async def __handle_remove_selected_profile_from_test(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to remove the Profile {self.model.selected_profile_name!r}"
                        f" from Test {self.model.current_test_short_name!r}?"),
                view_anchor=event.triggering_view):
            self.model.handle_remove_profile_from_test(self.model.selected_profile_name, self.model.test)
