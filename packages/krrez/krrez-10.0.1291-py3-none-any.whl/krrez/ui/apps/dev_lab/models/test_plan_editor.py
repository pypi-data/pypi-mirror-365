# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve

import krrez.api
import krrez.coding
import krrez.flow.bit_loader
import krrez.ui.apps.dev_lab.models.main


class TestPlanEditor(klovve.model.Model):

    test_plan: type[krrez.api.Bit]|None = klovve.model.property()

    all_test_names: list[str] = klovve.model.list_property()

    all_test_plan_names: list[str] = klovve.model.list_property()

    all_profile_test_names: list[str] = klovve.model.list_property()

    selected_test_name: str|None = klovve.model.property()

    selected_test_plan_name: str|None = klovve.model.property()

    selected_profile_name: str|None = klovve.model.property()

    def _(self):
        if self.test_plan:
            return krrez.coding.TestPlans.bit_name_to_test_plan_name(krrez.flow.bit_loader.bit_name(self.test_plan))
    current_test_plan_short_name: str|None = klovve.model.computed_property(_)

    def _(self):
        return self.__test_names_from_test_plan(self.test_plan) if self.test_plan else []
    current_test_plan_tests: t.Sequence[str] = klovve.model.computed_property(_)

    def _(self):
        return self.__test_plan_names_from_test_plan(self.test_plan) if self.test_plan else []
    current_test_plan_test_plans: t.Sequence[str] = klovve.model.computed_property(_)

    def _(self):
        return self.__profile_test_names_from_test_plan(self.test_plan) if self.test_plan else []
    current_test_plan_profiles: t.Sequence[str] = klovve.model.computed_property(_)

    def _(self):
        return f"Test Plan {self.current_test_plan_short_name!r}"
    header_text: str = klovve.model.computed_property(_)

    def __test_names_from_test_plan(self, test_plan: type[krrez.api.Bit]) -> t.Iterable[str]:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            return test_plan_code.tests

    def __profile_test_names_from_test_plan(self, test_plan: type[krrez.api.Bit]) -> t.Iterable[str]:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            return test_plan_code.profile_tests

    def __test_plan_names_from_test_plan(self, test_plan: type[krrez.api.Bit]) -> t.Iterable[str]:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            return test_plan_code.test_plans

    def _(self):
        return f"Remove {self.selected_test_name!r} from Test Plan"
    _remove_selected_test_button_text: str = klovve.model.computed_property(_)

    def _(self):
        return bool(self.selected_test_name)
    _remove_selected_test_button_is_visible: bool = klovve.model.computed_property(_)

    def _(self):
        return f"Remove {self.selected_test_plan_name!r} from Test Plan"
    _remove_selected_test_plan_button_text: str = klovve.model.computed_property(_)

    def _(self):
        return bool(self.selected_test_plan_name)
    _remove_selected_test_plan_button_is_visible: bool = klovve.model.computed_property(_)

    def _(self):
        return f"Remove {self.selected_profile_name!r} from Test Plan"
    _remove_selected_test_profile_button_text: str = klovve.model.computed_property(_)

    def _(self):
        return bool(self.selected_profile_name)
    _remove_selected_test_profile_button_is_visible: bool = klovve.model.computed_property(_)

    def handle_remove_test_plan(self, test_plan: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveTestPlanEvent(test_plan))

    def handle_add_test_to_test_plan(self, test_name: str, test_plan: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.AddTestToTestPlanEvent(test_name, test_plan))
        self.__refresh()

    def handle_remove_test_from_test_plan(self, test_name: str, test_plan: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveTestFromTestPlanEvent(test_name, test_plan))
        self.__refresh()

    def handle_add_test_plan_to_test_plan(self, test_plan_name: str, test_plan: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.AddTestPlanToTestPlanEvent(test_plan_name, test_plan))
        self.__refresh()

    def handle_remove_test_plan_from_test_plan(self, test_plan_name: str, test_plan: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveTestPlanFromTestPlanEvent(test_plan_name, test_plan))
        self.__refresh()

    def handle_add_test_profile_to_test_plan(self, profile_name: str, test_plan: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.AddTestProfileToTestPlanEvent(profile_name, test_plan))
        self.__refresh()

    def handle_remove_profile_from_test_plan(self, profile_name: str, test_plan: type[krrez.api.Bit]) -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveTestProfileFromTestPlanEvent(profile_name,
                                                                                                test_plan))
        self.__refresh()

    def __refresh(self) -> None:
        test_plan = self.test_plan
        self.test_plan = None
        self.test_plan = test_plan
