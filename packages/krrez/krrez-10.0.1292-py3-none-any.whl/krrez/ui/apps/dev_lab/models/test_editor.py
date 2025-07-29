# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve

import krrez.api
import krrez.coding
import krrez.flow.bit_loader
import krrez.ui.apps.dev_lab.models.main


class TestEditor(klovve.model.Model):

    test_class: type[krrez.api.Bit]|None = klovve.model.property()

    def _(self):
        return self.test_class() if self.test_class else None
    test: krrez.api.Bit|None = klovve.model.computed_property(_)

    selected_profile_name: str|None = klovve.model.property()

    all_profile_test_names: list[str] = klovve.model.list_property()

    def _(self):
        return self.__profile_names_from_test(self.test) if self.test else []
    current_test_profiles: list[str] = klovve.model.computed_property(_)

    def _(self):
        if self.test:
            return krrez.coding.Tests.bit_name_to_test_name(krrez.flow.bit_loader.bit_name(self.test))
    current_test_short_name: str|None = klovve.model.computed_property(_)

    def _(self):
        return f"Test {self.current_test_short_name!r}"
    header_text: str = klovve.model.computed_property(_)

    def __profile_names_from_test(self, test: type[krrez.api.Bit]) -> t.Sequence[str]:
        with krrez.coding.Tests.editor_for_test(test) as test_code:
            return test_code.profile_names or ()

    def handle_remove_test(self, test: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveTestEvent(test))

    def handle_add_profile_to_test(self, profile_name: str, test: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.AddProfileToTestEvent(profile_name, test))
        self.__refresh()

    def handle_remove_profile_from_test(self, profile_name: str, test: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveProfileFromTestEvent(profile_name, test))
        self.__refresh()

    def _(self):
        return f"Remove {self.selected_profile_name!r} from Test"
    _remove_selected_profile_button_text: str = klovve.model.computed_property(_)

    def _(self):
        return bool(self.selected_profile_name)
    _remove_selected_profile_button_is_visible: bool = klovve.model.computed_property(_)

    def __refresh(self) -> None:
        test_class = self.test_class
        self.test_class = None
        self.test_class = test_class
