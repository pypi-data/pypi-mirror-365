# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve

import krrez.ui.models.property_panel
import krrez.ui.views.property_panel
import krrez.ui.apps.seeding.models.new_seeding


class NewSeeding(klovve.ui.ComposedView[krrez.ui.apps.seeding.models.new_seeding.NewSeeding]):

    def _(self):
        if not self.model:
            return None
        if len(self.model.selected_profile_open_parameters) > 0:
            return krrez.ui.views.property_panel.PropertyPanel(
                model=krrez.ui.models.property_panel.PropertyPanel(
                    properties=self.model.bind.selected_profile_open_parameters,
                    values=self.model.bind.additional_seed_config))
    view_for_open_parameters = klovve.ui.computed_property(_)

    def compose(self):
        return klovve.views.Scrollable(
            body=klovve.views.Form(
                sections=[
                    klovve.views.Label(
                        text="Create Krrez installation media here, like USB sticks or SD cards, with a profile that is"
                             " customized for a particular use case."),
                    klovve.views.Label(
                        text="Note that its primary purpose is to set up real production machines, while there is also"
                             " the virtual machine based Testing feature for development."),
                    klovve.views.Form.Section(
                        label="Please choose the profile that you want to create an installation medium for.",
                        body=klovve.views.DropDown(
                            items=self.model.bind.all_profiles,
                            selected_item=self.model.bind.selected_profile,
                            item_label_func=lambda profile: profile.name)),
                    klovve.views.Placeholder(body=self.bind.view_for_open_parameters),
                    klovve.views.Form.Section(
                        label="Please choose the destination device. Everything on this device will be overwritten!",
                        body=klovve.views.DropDown(
                            items=self.model.bind.all_target_devices,
                            selected_item=self.model.bind.selected_target_device,
                            item_label_func=lambda target: target.label)),
                    klovve.views.Form.Section(
                            body=klovve.views.Button(
                                text="Seed",
                                action_name="start_seed",
                                is_enabled=self.model.bind.is_form_valid))],
                horizontal_layout=klovve.ui.Layout(klovve.ui.Align.CENTER),
                vertical_layout=klovve.ui.Layout(klovve.ui.Align.CENTER)))

    @klovve.event.action("start_seed")
    def __start_seed(self, event):
        event.stop_processing()
        self.trigger_event(StartSeedEvent())


class StartSeedEvent(klovve.event.Event):
    pass


# TODO  "store settings as profile for later" button
