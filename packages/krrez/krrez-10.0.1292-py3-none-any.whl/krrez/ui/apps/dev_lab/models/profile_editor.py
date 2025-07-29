# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.api
import krrez.coding
import krrez.flow.bit_loader
import krrez.seeding.profile_loader
import krrez.ui.apps.dev_lab.models.main


class ProfileEditor(klovve.model.Model):

    profile: "krrez.ui.apps.dev_lab.models.main.TProfileTuple|None" = klovve.model.property()

    selected_bit_name: str|None = klovve.model.property()

    all_normal_bits: list[type[krrez.api.Bit]] = klovve.model.list_property()

    def _(self):
        return (self.__bit_names_from_profile(self.profile[0]) or []) if self.profile else []
    current_profile_bits: list[str] = klovve.model.computed_property(_)

    def _(self):
        return f"Profile {self.profile[0].name!r}" if self.profile else ""
    header_text: str = klovve.model.computed_property(_)

    def _(self):
        return f"Remove {self.selected_bit_name!r} from Profile"
    _remove_selected_bit_button_text: str = klovve.model.computed_property(_)

    def _(self):
        return bool(self.selected_bit_name)
    _remove_selected_bit_button_is_visible: bool = klovve.model.computed_property(_)

    def __bit_names_from_profile(self, profile: type[krrez.api.Profile]) -> list[str]|None:
        with krrez.coding.Profiles.editor_for_profile(profile) as profile_code:
            return profile_code.krrez_bits

    def handle_remove_profile(self, profile_tuple: "krrez.ui.apps.dev_lab.models.main.TProfileTuple") -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveProfileEvent(profile_tuple[0], profile_tuple[1]))

    def handle_add_bit_to_profile(self, bit_name: str, profile_tuple: "krrez.ui.apps.dev_lab.models.main.TProfileTuple") -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.AddBitToProfileEvent(bit_name, profile_tuple[0]))
        self.__refresh()

    def handle_remove_bit_from_profile(self, bit_name: str, profile_tuple: "krrez.ui.apps.dev_lab.models.main.TProfileTuple") -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveBitFromProfileEvent(bit_name, profile_tuple[0]))
        self.__refresh()

    def __refresh(self) -> None:
        profile = self.profile
        self.profile = None
        self.profile = profile
