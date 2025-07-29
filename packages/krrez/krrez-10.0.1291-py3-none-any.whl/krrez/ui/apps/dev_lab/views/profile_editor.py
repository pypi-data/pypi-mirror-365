# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow.bit_loader
import krrez.seeding.profile_loader
import krrez.ui.apps.dev_lab.models.profile_editor


class ProfileEditor(klovve.ui.ComposedView[krrez.ui.apps.dev_lab.models.profile_editor.ProfileEditor]):

    def compose(self):
        if self.model.profile:
            return klovve.views.Scrollable(
                item=klovve.views.Form(
                    items=[
                        klovve.views.Label(text=self.model.bind.header_text),
                        *([
                              klovve.views.Form.Section(
                                  label="This profile will install the following Bits:",
                                  body=klovve.views.VerticalBox(items=[
                                      klovve.views.List(
                                          items=self.model.bind.current_profile_bits,
                                          selected_item=self.model.bind.selected_bit_name),
                                      klovve.views.Button(text=self.model.bind._remove_selected_bit_button_text,
                                                          is_visible=self.model.bind._remove_selected_bit_button_is_visible,
                                                          action_name="remove_selected_bit_from_profile"),
                                      klovve.views.Button(text="Add a Bit", action_name="add_a_bit_to_profile")])),
                        ] if (self.model.current_profile_bits is not None) else []),
                        klovve.views.Form.Section(
                            label="If you want to make any changes to this Profile, modify its code in this file:",
                            body=klovve.views.Label(
                                text=str(krrez.seeding.profile_loader.profile_module_path(self.model.profile[0])))),
                        *([
                            klovve.views.Form.Section(
                                label="There is also another file, which is relevant for testing, especially when you"
                                      " want to customize testing related things:",
                                body=klovve.views.Label(
                                    text=str(krrez.flow.bit_loader.bit_module_path(self.model.profile[1]))),
                            ),
                        ] if self.model.profile[1] else []),
                        klovve.views.Form.Section(
                            body=klovve.views.Button(text="Remove this Profile", action_name="remove_profile"))]))

    @klovve.event.action("remove_profile")
    async def __handle_remove_profile(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to delete the Profile {self.profile[0].name!r}?"),
                view_anchor=event.triggering_view):
            self.model.handle_remove_profile(self.model.profile)

    @klovve.event.action("add_a_bit_to_profile")
    async def __handle_add_a_bit_to_profile(self, event):
        if bit := await self.application.dialog(klovve.views.interact.Message(
                message="Please pick the Bit you want to add.",
                choices=[x.name for x in self.model.all_normal_bits]),
                view_anchor=event.triggering_view):
            self.model.handle_add_bit_to_profile(bit.name, self.model.profile)

    @klovve.event.action("remove_selected_bit_from_profile")
    async def __handle_remove_selected_bit_from_profile(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to delete the Bit {self.selected_bit_name!r}"
                        f" from Profile {self.model.profile[0].name!r}?"), view_anchor=event.triggering_view):
            self.model.handle_remove_bit_from_profile(self.model.selected_bit_name, self.model.profile)
