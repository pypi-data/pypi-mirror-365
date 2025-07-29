# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t
import klovve

import krrez.api
import krrez.ui.apps.seeding.models.main


class NewSeeding(klovve.model.Model):

    all_profiles: list["krrez.ui.apps.seeding.models.main.Profile"] = klovve.model.list_property()

    selected_profile: "krrez.ui.apps.seeding.models.main.Profile|None" = klovve.model.property()

    all_target_devices: list["krrez.ui.apps.seeding.models.main.Target"] = klovve.model.list_property()

    selected_target_device: "krrez.ui.apps.seeding.models.main.Target|None" = klovve.model.property()

    selected_profile_open_parameters: list["krrez.api.Profile.Parameter"] = klovve.model.list_property()

    additional_seed_config: dict["krrez.api.Profile.Parameter", t.Any] = klovve.model.property(initial=lambda: {})

    def _(self):
        return self.selected_profile and self.selected_target_device and all([
            self.additional_seed_config.get(profile_open_parameter)
            for profile_open_parameter in self.selected_profile_open_parameters])
    is_form_valid: bool = klovve.model.computed_property(_)
