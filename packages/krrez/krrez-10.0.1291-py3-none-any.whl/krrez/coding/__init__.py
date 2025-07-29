# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Understand and modify some Krrez specific code patterns, like :py:class:`krrez.api.Bit` implementations.

This is used by applications like the Development Lab.
"""
import json
import re
import typing as t

import hallyd

import krrez.api
import krrez.flow.bit_loader


class Bits:
    """
    Code actions on :py:class:`krrez.api.Bit` implementations.
    """

    #: The name of the default apply method.
    APPLY_METHOD_NAME = "__apply__"

    @staticmethod
    def apply_method_name_to_name(apply_method_name: str) -> t.Optional[str]:
        if apply_method_name == Bits.APPLY_METHOD_NAME:
            return None
        if not Bits.is_special_apply_method_name(apply_method_name):
            raise ValueError(f"not a valid apply method name: '{apply_method_name}'")
        return apply_method_name[len(Bits.APPLY_SPECIAL_METHOD_NAME_PREFIX):-len(Bits.APPLY_SPECIAL_METHOD_NAME_POSTFIX)]

    @staticmethod
    def is_bit_name_for_normal_bit(bit_name: str) -> bool:
        if Tests.is_bit_name_for_test(bit_name):
            return False
        if TestPlans.is_bit_name_for_test_plan(bit_name):
            return False
        if ProfileTests.is_bit_name_for_profile_test(bit_name):
            return False
        if ProfileTests.is_bit_name_for_profile_test_seed(bit_name):
            return False
        if bit_name.startswith("seed."):
            return False
        return True

    @staticmethod
    def is_special_apply_method_name(name: str) -> bool:
        return (name.startswith(Bits.APPLY_SPECIAL_METHOD_NAME_PREFIX)
                and name[len(Bits.APPLY_SPECIAL_METHOD_NAME_PREFIX)+1:].endswith(Bits.APPLY_SPECIAL_METHOD_NAME_POSTFIX))

    @staticmethod
    def editor_for_bit(bit: "krrez.api.Bit|type[krrez.api.Bit]") -> "Bits._Editor":
        return Bits._Editor(krrez.flow.bit_loader.bit_name(bit), krrez.flow.bit_loader.bit_module_path(bit))

    @staticmethod
    def editor_for_new_bit(bit_name, module_base_directory: hallyd.fs.Path) -> "Bits._Editor":
        return Bits._Editor(bit_name, module_base_directory)

    class _Editor(hallyd.coding.Editor):

        def __init__(self, bit_name: str, module_base_directory: hallyd.fs.Path):
            self.__rootpath = _module_root_directory(module_base_directory)("krrez/bits", bit_name.replace(".", "/"))
            super().__init__(self.__rootpath("__init__.py"))

        def create(self) -> None:
            self.code = ""
            self.add_import("krrez.api")
            new_class = self.add_class("Bit", derived_from="krrez.api.Bit",
                                       docstring=f"{hallyd.coding.TBD_TAG} add a brief description of what this Bit"
                                                 f" does here")
            new_class.add_method(
                f'def {Bits.APPLY_METHOD_NAME}(self):\n'
                f'    self._log.message.info("Hello, World!")')


class Profiles:
    """
    Code actions on :py:class:`krrez.api.Profile` implementations.
    """

    @staticmethod
    def editor_for_profile(profile: type["krrez.api.Profile"]) -> "Profiles._Editor":
        import krrez.seeding.profile_loader
        module_path = krrez.seeding.profile_loader.profile_module_path(profile)
        return Profiles._Editor(module_path.name[:-3], module_path)  # TODO

    @staticmethod
    def editor_for_new_profile(profile_name: str, module_base_directory: hallyd.fs.Path) -> "Profiles._Editor":
        return Profiles._Editor(profile_name, module_base_directory)

    class _Editor(hallyd.coding.Editor):

        _KRREZ_BITS_PATTERN = re.compile(r"krrez_bits\s*=\s*(\[[^]]*])")

        def __init__(self, profile_name: str, module_base_directory: hallyd.fs.Path):
            self.__rootpath = _module_root_directory(module_base_directory)(f"krrez/profiles/{profile_name}.py")
            super().__init__(self.__rootpath)

        def create(self) -> None:
            self.code = ""
            self.add_import("krrez.profiles.cloud")
            self.add_class("Profile", derived_from="krrez.profiles.cloud.Profile",
                           docstring=f"{hallyd.coding.TBD_TAG} add a brief description of what this Profile is for"
                                     f" here").add_method(
                'def __init__(self, *, hostname: str):\n'
                '    super().__init__(\n'
                '        hostname=hostname,\n'
                '        arch="x86_64",\n'
                '        krrez_bits=[],\n'
                '        config={}\n'
                '    )\n')

        @property
        def krrez_bits(self) -> t.Optional[t.Iterable[str]]:
            match = self._KRREZ_BITS_PATTERN.search(self.code)
            if not match:
                return None
            bitstest = match.group(1)
            bitstest = "[" + bitstest.strip("[]").strip().strip(",") + "]"  # TODO (comma in the end is bad otherwise)
            try:
                return tuple([str(piece) for piece in json.loads(bitstest)])
            except (json.JSONDecodeError, TypeError):
                return None

        def __change_bits(self, change_list_func):
            bit_names_for_profile = self.krrez_bits
            if bit_names_for_profile is None:
                return  # TODO error handling?!
            bit_names_for_profile = change_list_func(bit_names_for_profile)
            # TODO streamline/combine with __bit_names_from_profile
            match = self._KRREZ_BITS_PATTERN.search(self.code)
            self.code = self.code[:match.start(1)] + json.dumps(bit_names_for_profile) + self.code[match.end(1):]

        def add_krrez_bit(self, bit_name: str) -> None:
            def change_list(bit_names_for_profile):
                if bit_name not in bit_names_for_profile:
                    bit_names_for_profile.append(bit_name)
            self.__change_bits(change_list)

        def remove_krrez_bit(self, bit_name: str) -> None:
            def change_list(bit_names_for_profile):
                if bit_name in bit_names_for_profile:
                    bit_names_for_profile.remove(bit_name)
            self.__change_bits(change_list)


class ProfileTests:
    """
    Code actions on Profile Tests (:py:class:`krrez.api.Bit` implementations with a special name).
    """

    PROFILE_TEST_NAME_TO_BIT_NAME_PREFIX = "zz_test.zz_profiles."
    PROFILE_TEST_NAME_TO_SEED_BIT_NAME_POSTFIX = ".seed"

    @staticmethod
    def is_bit_name_for_profile_test(bit_name: str) -> bool:
        return (bit_name.startswith(ProfileTests.PROFILE_TEST_NAME_TO_BIT_NAME_PREFIX)
                and ("." not in bit_name[len(ProfileTests.PROFILE_TEST_NAME_TO_BIT_NAME_PREFIX):]))

    @staticmethod
    def is_bit_name_for_profile_test_seed(bit_name: str) -> bool:
        if not bit_name.endswith(ProfileTests.PROFILE_TEST_NAME_TO_SEED_BIT_NAME_POSTFIX):
            return False
        return ProfileTests.is_bit_name_for_profile_test(
            bit_name[:-len(ProfileTests.PROFILE_TEST_NAME_TO_SEED_BIT_NAME_POSTFIX)])

    @staticmethod
    def bit_name_to_profile_test_name(bit_name: str) -> str:
        return _bit_name_to_specific_name(bit_name,
                                          bit_to_specific_prefix=ProfileTests.PROFILE_TEST_NAME_TO_BIT_NAME_PREFIX,
                                          error_message="Not a valid bit name for a Profile Test")

    @staticmethod
    def profile_test_name_to_bit_name(profile_test_name: str) -> str:
        return ProfileTests.PROFILE_TEST_NAME_TO_BIT_NAME_PREFIX + profile_test_name

    @staticmethod
    def bit_name_to_profile_test_seed_name(bit_name: str) -> str:
        if not bit_name.endswith(ProfileTests.PROFILE_TEST_NAME_TO_SEED_BIT_NAME_POSTFIX):
            raise ValueError(f"not a valid bit name for a Profile Test Seed: {bit_name}")
        return ProfileTests.bit_name_to_profile_test_name(bit_name[:-len(ProfileTests.PROFILE_TEST_NAME_TO_SEED_BIT_NAME_POSTFIX)])

    @staticmethod
    def profile_test_seed_name_to_bit_name(profile_test_seed_name: str) -> str:
        return ProfileTests.profile_test_name_to_bit_name(profile_test_seed_name) + ProfileTests.PROFILE_TEST_NAME_TO_SEED_BIT_NAME_POSTFIX

    @staticmethod
    def editor_for_new_profile_test(profile_test_name: str,
                                    module_base_directory: hallyd.fs.Path) -> "ProfileTests._Editor":
        return ProfileTests._Editor(profile_test_name, module_base_directory)

    @staticmethod
    def editor_for_profile_test(profile_test: "krrez.api.Bit|type[krrez.api.Bit]") -> "ProfileTests._Editor":
        return ProfileTests._Editor(ProfileTests.bit_name_to_profile_test_name(krrez.flow.bit_loader.bit_name(profile_test)),
                                    krrez.flow.bit_loader.bit_module_path(profile_test))

    class _Editor(hallyd.coding.Editor):

        def __init__(self, profile_name: str, module_base_directory: hallyd.fs.Path):
            self.__rootpath = _module_root_directory(module_base_directory)(f"krrez/bits/zz_test/zz_profiles"
                                                                            f"/{profile_name}.py")
            super().__init__(self.__rootpath)
            self.__profile_name = profile_name

        def create(self) -> None:
            self.code = ""
            self.add_import("krrez.api")
            self.add_import("krrez.bits.zz_test.zz_run")
            new_class = self.add_class("Bit", derived_from="krrez.api.Bit",
                                       docstring=f"The Test associated to Profile '{self.__profile_name}'.")
            new_class.add_method(
                f'@krrez.api._AfterwardsDependency(".testbundle")\n'
                f'def {Bits.APPLY_METHOD_NAME}(self):\n'
                f'    pass')
            new_class.add_method(
                f'@krrez.api._BeforehandDependency(".seed")\n'
                f'def {Bits.apply_method_name("prepare")}(self):\n'
                f'    with self._run.machine_configuration("{self.__profile_name}") as conf:\n'
                f'        conf.additional_config.update({{\n'
                f'            # {hallyd.coding.TBD_TAG} add config values for keys that are needed during seeding\n'
                f'        }})')
            new_class.add_method(
                f'def {Bits.apply_method_name("seed")}(self):\n'
                f'    self._run.seed_machine(self._run.machine("{self.__profile_name}"))')
            new_class.add_method(
                f'@krrez.api._BeforehandDependency(".seed")\n'
                f'def {Bits.apply_method_name("testbundle")}(self):\n'
                f'    pass')


class Tests:
    """
    Code actions on Tests (:py:class:`krrez.api.Bit` implementations with a special name).
    """

    TEST_NAME_TO_BIT_NAME_PREFIX = "zz_test."
    PROFILE_BIT_NAME_PREFIX = "In"

    @staticmethod
    def is_bit_name_for_test(bit_name: str) -> bool:
        if TestPlans.is_bit_name_for_test_plan(bit_name):
            return False
        if ProfileTests.is_bit_name_for_profile_test(bit_name):
            return False
        if ProfileTests.is_bit_name_for_profile_test_seed(bit_name):
            return False
        return bit_name.startswith(Tests.TEST_NAME_TO_BIT_NAME_PREFIX)

    @staticmethod
    def bit_name_to_test_name(bit_name: str) -> str:
        return _bit_name_to_specific_name(bit_name,
                                          bit_to_specific_prefix=Tests.TEST_NAME_TO_BIT_NAME_PREFIX,
                                          error_message="Not a valid bit name for a Test")

    @staticmethod
    def test_name_to_bit_name(test_name: str) -> str:
        return Tests.TEST_NAME_TO_BIT_NAME_PREFIX + test_name

    @staticmethod
    def editor_for_test(test: "krrez.api.Bit|type[krrez.api.Bit]") -> "Tests._Editor":
        return Tests._Editor(Tests.bit_name_to_test_name(krrez.flow.bit_loader.bit_name(test)), krrez.flow.bit_loader.bit_module_path(test))

    @staticmethod
    def editor_for_new_test(test_name: str, module_base_directory: hallyd.fs.Path) -> "Tests._Editor":
        return Tests._Editor(test_name, module_base_directory)

    class _Editor(hallyd.coding.Editor):

        def __init__(self, test_name: str, module_base_directory: hallyd.fs.Path):
            self.__rootpath = _module_root_directory(module_base_directory)("krrez/bits/zz_test",
                                                                            test_name.replace(".", "/"))
            super().__init__(self.__rootpath("__init__.py"))

        def create(self) -> None:
            self.code = ""
            self.add_import("krrez.testing.api")
            new_class = self.add_class("Bit", derived_from="krrez.testing.api.BundledTestBit",
                                       docstring=f"{hallyd.coding.TBD_TAG} add a brief description of what this Test"
                                                 f" checks here")
            new_class.add_method(
                'def __test(self, machine_name):\n'
                '    machine = self._run.machine(machine_name)\n'
                '    assert machine.exec(["printf", "hello"]) == "hello"')

        @property
        def profile_names(self) -> t.Optional[t.Iterable[str]]:
            my_prefix = "TODO Bits.APPLY_SPECIAL_METHOD_NAME_PREFIX" + Tests.PROFILE_BIT_NAME_PREFIX
            bit_class = self.class_by_name("Bit")
            result = []
            return ()#TODO weg
            for method in bit_class.methods:
                if method.name.startswith(my_prefix):
                    i1 = len(my_prefix)
                    i2 = method.name.find("_", i1)
                    if i2 > -1:
                        rname = method.name[i1:i2]
                        if rname not in result:
                            result.append(rname)
            return tuple(result)

        def add_profile(self, profile_name: str) -> None:
            if self.profile_names is None:  # TODO
                return
            bit_class = self.class_by_name("Bit")
            apply_method_name = Bits.apply_method_name(f"{Tests.PROFILE_BIT_NAME_PREFIX}{profile_name}_testbundle")
            bit_class.add_method(
                f'def {apply_method_name}(self):\n'
                f'    self.__test("{profile_name}")')

        def remove_profile(self, profile_name: str) -> None:
            if self.profile_names is None:  # TODO
                return
            for bit_method in self.class_by_name("Bit").methods:
                if bit_method.name.startswith(f"{Bits.APPLY_SPECIAL_METHOD_NAME_PREFIX}{Tests.PROFILE_BIT_NAME_PREFIX}"
                                              f"{profile_name}_"):
                    bit_method.remove()


class TestPlans:
    """
    Code actions on Test Plans (:py:class:`krrez.api.Bit` implementations with a special name).
    """

    TEST_PLAN_NAME_TO_BIT_NAME_PREFIX = "zz_test.zz_plans."

    @staticmethod
    def is_bit_name_for_test_plan(bit_name: str) -> bool:
        return (bit_name.startswith(TestPlans.TEST_PLAN_NAME_TO_BIT_NAME_PREFIX)
                and ("." not in bit_name[len(TestPlans.TEST_PLAN_NAME_TO_BIT_NAME_PREFIX):]))

    @staticmethod
    def bit_name_to_test_plan_name(bit_name: str) -> str:
        return _bit_name_to_specific_name(bit_name,
                                          bit_to_specific_prefix=TestPlans.TEST_PLAN_NAME_TO_BIT_NAME_PREFIX,
                                          error_message="Not a valid bit name for a Test Plan")

    @staticmethod
    def test_plan_name_to_bit_name(test_plan_name: str) -> str:
        return TestPlans.TEST_PLAN_NAME_TO_BIT_NAME_PREFIX + test_plan_name

    @staticmethod
    def editor_for_test_plan(test_plan: "krrez.api.Bit|type[krrez.api.Bit]") -> "TestPlans._Editor":
        return TestPlans._Editor(TestPlans.bit_name_to_test_plan_name(krrez.flow.bit_loader.bit_name(test_plan)),
                                 krrez.flow.bit_loader.bit_module_path(test_plan))

    @staticmethod
    def editor_for_new_test_plan(test_plan_name, module_base_directory: hallyd.fs.Path) -> "TestPlans._Editor":
        return TestPlans._Editor(test_plan_name, module_base_directory)

    class _Editor(hallyd.coding.Editor):

        def __init__(self, test_plan_name: str, module_base_directory: hallyd.fs.Path):
            self.__rootpath = _module_root_directory(module_base_directory)("krrez/bits/zz_test/zz_plans",
                                                                            test_plan_name.replace(".", "/"))
            super().__init__(self.__rootpath("__init__.py"))
            self.__test_plan_name = test_plan_name

        def create(self) -> None:
            self.code = ""
            self.add_import("krrez.api")
            new_class = self.add_class(
                "Bit", derived_from="krrez.api.Bit",
                docstring=f"{hallyd.coding.TBD_TAG} add a brief description of what this Test Plan does here")
            new_class.add_method(
                f'def {Bits.APPLY_METHOD_NAME}(self):\n'
                f'    pass')

        @property
        def tests(self) -> t.Iterable[str]:
            return []#TODO
            return self.__get_names(Tests.is_bit_name_for_test, Tests.bit_name_to_test_name)

        @property
        def test_plans(self) -> t.Iterable[str]:
            return []#TODO
            return self.__get_names(TestPlans.is_bit_name_for_test_plan, TestPlans.bit_name_to_test_plan_name)

        @property
        def profile_tests(self) -> t.Iterable[str]:
            return []#TODO
            return self.__get_names(ProfileTests.is_bit_name_for_profile_test, ProfileTests.bit_name_to_profile_test_name)

        def add_test(self, test_name: str) -> None:
            self.__add_dependency_decoration(Tests.test_name_to_bit_name(test_name))

        def remove_test(self, test_name: str) -> None:
            self.__remove_decoration(Tests.test_name_to_bit_name(test_name))

        def add_test_plan(self, test_plan_name: str) -> None:
            self.__add_dependency_decoration(TestPlans.test_plan_name_to_bit_name(test_plan_name))

        def remove_test_plan(self, test_plan_name: str) -> None:
            self.__remove_decoration(TestPlans.test_plan_name_to_bit_name(test_plan_name))

        def add_profile_test(self, profile_name: str) -> None:
            self.__add_dependency_decoration(ProfileTests.profile_test_name_to_bit_name(profile_name))

        def remove_profile_test(self, profile_name: str) -> None:
            self.__remove_decoration(ProfileTests.profile_test_name_to_bit_name(profile_name))

        def __get_names(self, bit_name_filter_func, bit_name_to_name_func):
            try:
                decorations = self.__apply_method().decorations
            except Exception:  # TODO
                return None
            result = []
            for decoration in decorations:
                bit_name = re.search(r'"(.*)"', decoration).group(1)
                if bit_name_filter_func(bit_name):
                    result.append(bit_name_to_name_func(bit_name))
            return result

        def __add_dependency_decoration(self, item_name):
            self.__apply_method().add_decoration(f'@krrez.api._BeforehandDependency("{item_name}")')

        def __remove_decoration(self, item_name):
            apply_method = self.__apply_method()
            for i_decoration, decoration in reversed(list(enumerate(apply_method.decorations))):
                if f'"{item_name}"' in decoration:  # TODO
                    apply_method.remove_decoration(i_decoration)

        def __apply_method(self):
            return self.class_by_name("Bit").method_by_name(Bits.APPLY_METHOD_NAME)


def _module_root_directory(path: hallyd.fs.Path) -> hallyd.fs.Path:  # TODO dedup
    if path("krrez").exists():
        return path
    while path.name != "krrez":
        path = path.parent
    return path.parent


def _bit_name_to_specific_name(bit_name: str, *, error_message: str, bit_to_specific_prefix: str) -> str:
    if not bit_name.startswith(bit_to_specific_prefix):
        raise ValueError(f"{error_message}: {bit_name}")
    return bit_name[len(bit_to_specific_prefix):]
