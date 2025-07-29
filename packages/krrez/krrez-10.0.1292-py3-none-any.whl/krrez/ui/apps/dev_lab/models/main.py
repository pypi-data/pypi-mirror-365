# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import contextlib
import dataclasses
import typing as t

import hallyd
import klovve

import krrez.api
import krrez.coding
import krrez.ui.models.list_panel
import krrez.ui.views.list_panel
import krrez.flow.bit_loader
import krrez.seeding.profile_loader


TProfileTuple = tuple[type[krrez.api.Profile], krrez.api.Bit|None]


@dataclasses.dataclass(frozen=True)
class Bit:
    name: str
    native: type[krrez.api.Bit]
    module_path: hallyd.fs.Path


class RemoveBitEvent(klovve.event.Event):

    def __init__(self, bit: Bit):
        super().__init__()
        self.bit = bit


class RemoveProfileEvent(klovve.event.Event):

    def __init__(self, profile: type[krrez.api.Profile], test_bit: type[krrez.api.Bit]|None):
        super().__init__()
        self.profile = profile
        self.test_bit = test_bit


class AddBitToProfileEvent(klovve.event.Event):

    def __init__(self, bit_name: str, profile: type[krrez.api.Profile]):
        super().__init__()
        self.bit_name = bit_name
        self.profile = profile


class RemoveBitFromProfileEvent(klovve.event.Event):

    def __init__(self, bit_name: str, profile: type[krrez.api.Profile]):
        super().__init__()
        self.bit_name = bit_name
        self.profile = profile


class RemoveTestPlanEvent(klovve.event.Event):

    def __init__(self, test_plan: type[krrez.api.Bit]):
        super().__init__()
        self.test_plan = test_plan


class AddTestToTestPlanEvent(klovve.event.Event):

    def __init__(self, test_name: str, test_plan: type[krrez.api.Bit]):
        super().__init__()
        self.test_name = test_name
        self.test_plan = test_plan


class RemoveTestFromTestPlanEvent(klovve.event.Event):

    def __init__(self, test_name: str, test_plan: type[krrez.api.Bit]):
        super().__init__()
        self.test_name = test_name
        self.test_plan = test_plan


class AddTestPlanToTestPlanEvent(klovve.event.Event):

    def __init__(self, test_plan_name: str, test_plan: type[krrez.api.Bit]):
        super().__init__()
        self.test_plan_name = test_plan_name
        self.test_plan = test_plan


class RemoveTestPlanFromTestPlanEvent(klovve.event.Event):

    def __init__(self, test_plan_name: str, test_plan: type[krrez.api.Bit]):
        super().__init__()
        self.test_plan_name = test_plan_name
        self.test_plan = test_plan


class AddTestProfileToTestPlanEvent(klovve.event.Event):

    def __init__(self, test_profile_name: str, test_plan: type[krrez.api.Bit]):
        super().__init__()
        self.test_profile_name = test_profile_name
        self.test_plan = test_plan


class RemoveTestProfileFromTestPlanEvent(klovve.event.Event):

    def __init__(self, test_profile_name: str, test_plan: type[krrez.api.Bit]):
        super().__init__()
        self.test_profile_name = test_profile_name
        self.test_plan = test_plan


class RemoveTestEvent(klovve.event.Event):

    def __init__(self, test: type[krrez.api.Bit]):
        super().__init__()
        self.test = test


class AddProfileToTestEvent(klovve.event.Event):

    def __init__(self, profile_name: str, test: type[krrez.api.Bit]):
        super().__init__()
        self.profile_name = profile_name
        self.test = test


class RemoveProfileFromTestEvent(klovve.event.Event):

    def __init__(self, profile_name: str, test: type[krrez.api.Bit]):
        super().__init__()
        self.profile_name = profile_name
        self.test = test


class Main(klovve.model.Model):

    krrez_application: krrez.ui.Application = klovve.model.property()

    selected_custom_bit: Bit|None = klovve.model.property()

    selected_custom_profile: TProfileTuple|None = klovve.model.property()

    selected_custom_test: type[krrez.api.Bit]|None = klovve.model.property()

    selected_custom_test_plan: type[krrez.api.Bit]|None = klovve.model.property()

    def _(self):
        if self.krrez_application:
            return self.krrez_application.runtime_data.all_bits
        return ()
    all_bits: list[type[krrez.api.Bit]] = klovve.model.computed_list_property(_)

    def _(self):
        return [Bit(name=krrez.flow.bit_loader.bit_name(bit), native=bit,
                    module_path=krrez.flow.bit_loader.bit_module_path(bit))
                for bit in self.all_bits
                if krrez.coding.Bits.is_bit_name_for_normal_bit(krrez.flow.bit_loader.bit_name(bit))
                and self.__is_custom_module(krrez.flow.bit_loader.bit_module_path(bit))]
    all_custom_bits: list[Bit] = klovve.model.computed_property(_)

    def _(self):
        available_custom_profiles = []
        for profile in krrez.seeding.profile_loader.all_profiles():
            if self.__is_custom_module(krrez.seeding.profile_loader.profile_module_path(profile)):
                profile_test_bit_name = krrez.coding.ProfileTests.profile_test_name_to_bit_name(profile.name)
                for bit in self.all_bits:
                    if krrez.flow.bit_loader.bit_name(bit) == profile_test_bit_name:
                        profile_test_bit = bit()
                        break
                else:
                    profile_test_bit = None
                available_custom_profiles.append((profile, profile_test_bit))
        available_custom_profiles.sort(key=lambda profile_tuple: profile_tuple[0].name)
        return available_custom_profiles
    all_custom_profiles: t.Sequence[TProfileTuple] = klovve.model.computed_property(_)

    def _(self):
        return [bit for bit in self.all_bits if krrez.coding.Tests.is_bit_name_for_test(krrez.flow.bit_loader.bit_name(bit))
                and self.__is_custom_module(krrez.flow.bit_loader.bit_module_path(bit))]
    all_custom_tests: list[type[krrez.api.Bit]] = klovve.model.computed_property(_)

    def _(self):
        return [bit for bit in self.all_bits if krrez.coding.TestPlans.is_bit_name_for_test_plan(krrez.flow.bit_loader.bit_name(bit))
                and self.__is_custom_module(krrez.flow.bit_loader.bit_module_path(bit))]
    all_custom_test_plans: list[type[krrez.api.Bit]] = klovve.model.computed_property(_)

    def _(self):
        return [bit for bit in self.all_bits if krrez.coding.Bits.is_bit_name_for_normal_bit(krrez.flow.bit_loader.bit_name(bit))]
    all_normal_bits: list[type[krrez.api.Bit]] = klovve.model.computed_property(_)

    def _(self):
        return [krrez.coding.Tests.bit_name_to_test_name(krrez.flow.bit_loader.bit_name(bit)) for bit in self.all_bits
                if krrez.coding.Tests.is_bit_name_for_test(krrez.flow.bit_loader.bit_name(bit))]
    all_test_names: list[str] = klovve.model.computed_property(_)

    def _(self):
        return [krrez.coding.TestPlans.bit_name_to_test_plan_name(krrez.flow.bit_loader.bit_name(bit)) for bit in self.all_bits
                if krrez.coding.TestPlans.is_bit_name_for_test_plan(krrez.flow.bit_loader.bit_name(bit))]
    all_test_plan_names: list[str] = klovve.model.computed_property(_)

    def _(self):
        return [krrez.coding.ProfileTests.bit_name_to_profile_test_seed_name(krrez.flow.bit_loader.bit_name(bit)) for bit in self.all_bits
                if krrez.coding.ProfileTests.is_bit_name_for_profile_test_seed(krrez.flow.bit_loader.bit_name(bit))]
    all_profile_test_names: list[str] = klovve.model.computed_property(_)

    def __create_bit(self, module_base_directory: krrez.api.Path, bit_name: str) -> None:
        with krrez.coding.Bits.editor_for_new_bit(bit_name, module_base_directory) as bit_code:
            bit_code.create()
        self.app.refresh_all_bits()

    def __create_profile(self, module_base_directory: krrez.api.Path, profile_name: str) -> None:
        with krrez.coding.Profiles.editor_for_new_profile(profile_name, module_base_directory) as profile_code:
            profile_code.create()
        with krrez.coding.ProfileTests.editor_for_new_profile_test(profile_name, module_base_directory) as profiletest_code:
            profiletest_code.create()
        self.app.refresh_all_bits()

    def __create_test(self, module_base_directory: krrez.api.Path, test_name: str) -> None:
        with krrez.coding.Tests.editor_for_new_test(test_name, module_base_directory) as test_code:
            test_code.create()
        self.app.refresh_all_bits()

    def __create_test_plan(self, module_base_directory: krrez.api.Path, test_plan_name: str) -> None:
        with krrez.coding.TestPlans.editor_for_new_test_plan(test_plan_name, module_base_directory) as test_plan_code:
            test_plan_code.create()
        self.app.refresh_all_bits()

    def handle_remove_bit(self, bit: Bit) -> None:
        self.__remove_for_editor(krrez.coding.Bits.editor_for_bit(bit.native))
        self.app.refresh_all_bits()

    def handle_remove_profile(self, profile: type[krrez.api.Profile], test_bit: type[krrez.api.Bit]|None) -> None:
        self.__remove_for_editor(krrez.coding.Profiles.editor_for_profile(profile))
        if test_bit:
            self.__remove_for_editor(krrez.coding.ProfileTests.editor_for_profile_test(test_bit))
        self.app.refresh_all_bits()

    def handle_remove_test(self, test: type[krrez.api.Bit]) -> None:
        self.__remove_for_editor(krrez.coding.Tests.editor_for_test(test))
        self.app.refresh_all_bits()

    def handle_remove_test_plan(self, test_plan: type[krrez.api.Bit]) -> None:
        self.__remove_for_editor(krrez.coding.TestPlans.editor_for_test_plan(test_plan))
        self.app.refresh_all_bits()

    def handle_add_bit_to_profile(self, bit_name: str, profile: type[krrez.api.Profile]) -> None:
        with krrez.coding.Profiles.editor_for_profile(profile) as profile_code:
            profile_code.add_krrez_bit(bit_name)

    def handle_remove_bit_from_profile(self, bit_name: str, profile: type[krrez.api.Profile]) -> None:
        with krrez.coding.Profiles.editor_for_profile(profile) as profile_code:
            profile_code.remove_krrez_bit(bit_name)

    def handle_add_test_to_test_plan(self, test_name: str, test_plan: type[krrez.api.Bit]) -> None:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            test_plan_code.add_test(test_name)

    def handle_remove_test_from_test_plan(self, test_name: str, test_plan: type[krrez.api.Bit]) -> None:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            test_plan_code.remove_test(test_name)

    def handle_add_test_plan_to_test_plan(self, test_plan_name: str, test_plan: type[krrez.api.Bit]) -> None:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            test_plan_code.add_test_plan(test_plan_name)

    def handle_remove_test_plan_from_test_plan(self, test_plan_name: str, test_plan: type[krrez.api.Bit]) -> None:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            test_plan_code.remove_test_plan(test_plan_name)

    def handle_add_profile_test_to_test_plan(self, test_profile_name: str, test_plan: type[krrez.api.Bit]) -> None:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            test_plan_code.add_profile_test(test_profile_name)

    def handle_remove_profile_test_from_test_plan(self, test_profile_name: str, test_plan: type[krrez.api.Bit]) -> None:
        with krrez.coding.TestPlans.editor_for_test_plan(test_plan) as test_plan_code:
            test_plan_code.remove_profile_test(test_profile_name)

    def handle_add_profile_to_test(self, profile_name: str, test: type[krrez.api.Bit]) -> None:
        with krrez.coding.Tests.editor_for_test(test) as test_code:
            test_code.add_profile(profile_name)

    def handle_remove_profile_from_test(self, profile_name: str, test: type[krrez.api.Bit]) -> None:
        with krrez.coding.Tests.editor_for_test(test) as test_code:
            test_code.remove_profile(profile_name)

    def handle_create_new_bit(self, krrez_module_directory: hallyd.fs.Path, new_name: str) -> None:
        self.__create_bit(krrez_module_directory, new_name)

    def handle_create_new_profile(self, krrez_module_directory: hallyd.fs.Path, new_name: str) -> None:
        self.__create_profile(krrez_module_directory, new_name)

    def handle_create_new_test_plan(self, krrez_module_directory: hallyd.fs.Path, new_name: str) -> None:
        self.__create_test_plan(krrez_module_directory, new_name)

    def handle_create_new_test(self, krrez_module_directory: hallyd.fs.Path, new_name: str) -> None:
        self.__create_test(krrez_module_directory, new_name)

    def __remove_for_editor(self, editor: hallyd.coding.Editor) -> None:
        editor.path.remove()

    @staticmethod
    def __is_custom_module(path: hallyd.fs.Path) -> bool:
        return any(path.is_relative_to(module_dir_path) for module_dir_path
                   in krrez.flow.bit_loader.krrez_module_directories(with_builtin=False))
