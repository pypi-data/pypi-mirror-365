# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Main programming interface for the implementation of testing bits.
"""
import abc
import importlib

import krrez.api.internal
import krrez.bits.zz_test.zz_run
import krrez.coding
import krrez.flow.bit_loader
import krrez.testing.landmark


class _InitDep(krrez.api.internal.Dependency):

    # noinspection PyUnusedLocal
    def manipulate_resolution_plan(self, owning_bit, plan):
        mymod = importlib.import_module(owning_bit.__module__)
        if owning_bit.__name__ == "Bit":
            for itm_name in dir(mymod):
                itm = getattr(mymod, itm_name)
                if isinstance(itm, type) and issubclass(itm, krrez.api.Bit):
                    if itm_name.endswith("Bit") and itm_name != "Bit":
                        bname = itm_name[:-len("Bit")]
                        if bname.startswith(krrez.coding.Tests.PROFILE_BIT_NAME_PREFIX):
                            attr_short_name = bname[len(krrez.coding.Tests.PROFILE_BIT_NAME_PREFIX):]
                            profile_name, _, testbundle_name = attr_short_name.partition("TestBundle")
                            if not testbundle_name:
                                raise RuntimeError(f"the test bit name '{itm_name}' is invalid")
                            profile_name = profile_name.lower()
                            testbundle_name = f"TestBundle{testbundle_name}"
                            if not any(filter(lambda x: isinstance(x, _InstallBeforehandForTestBundle)
                                                        and x.profile_name == profile_name
                                                        and x.testbundle_name == testbundle_name,
                                              plan.dependencies_for_bit(owning_bit))):
                                plan.dependencies_for_bit(owning_bit).append(
                                    _InstallBeforehandForTestBundle(krrez.flow.bit_loader.bit_full_name(owning_bit).rpartition(".")[0][len(krrez.flow.BITS_NAMESPACE)+1:] + "." + itm_name,
                                                                    profile_name=profile_name, testbundle_name=testbundle_name))
                                return True
        else:
            myname = owning_bit.__name__
            bname = myname[:-len("Bit")]
            if bname.startswith(krrez.coding.Tests.PROFILE_BIT_NAME_PREFIX):
                attr_short_name = bname[len(krrez.coding.Tests.PROFILE_BIT_NAME_PREFIX):]
                profile_name, _, testbundle_name = attr_short_name.partition("TestBundle")
                if not testbundle_name:
                    raise RuntimeError(f"the test bit name '{myname}' is invalid")
                profile_name = profile_name.lower()
                testbundle_name = f"TestBundle{testbundle_name}"
            profile_test_bit_name = krrez.coding.ProfileTests.profile_test_name_to_bit_name(profile_name)
            bundle_bit_name = f"{profile_test_bit_name}.{testbundle_name}Bit"
            if not any(filter(lambda x: isinstance(x, _PartOf) and x.bit_name == bundle_bit_name,
                              plan.dependencies_for_bit(owning_bit))):
                plan.dependencies_for_bit(owning_bit).append(_PartOf(bundle_bit_name))
                return True


class BundledTestBit(krrez.api.Bit):
    """
    Base class for simple implementation of test bundle oriented tests.

    Use it this way (all in your test module):
    - Implement a subclass of it, named "`Bit`". It usually contains only the `._prepare()` and `._test()` methods.
    - For each test bundle that your test is relevant for, implement a subclass of your `Bit`, named e.g.
      "`InDonkeyTestBundle1Bit`". In its :py:meth:`krrez.api.Bit.__apply__` methods, call `self._prepare()` and
      `self._test()` how it makes sense.
    """

    _run: krrez.bits.zz_test.zz_run.Bit

    __init_dep: _InitDep()


class LandmarkBit(krrez.api.Bit, abc.ABC):
    """
    Base class for landmarks.
    """

    _run: krrez.bits.zz_test.zz_run.Bit

    @abc.abstractmethod
    def _after_reboot_handler(self) -> "AfterRebootHandler":
        pass

    def __apply__(self):
        krrez.testing.landmark.set_landmark(self._run, self._after_reboot_handler(), type(self).__name__)


class AfterRebootHandler(abc.ABC):

    @abc.abstractmethod
    def after_reboot(self, machine_name: str) -> None:
        pass


class _PartOf(krrez.api.internal.BaseForSimpleBehaviorDependency):

    def __init__(self, bit_name: str):
        super().__init__([bit_name], afterwards=False)
        self.__bit_name = bit_name

    @property
    def bit_name(self) -> str:
        return self.__bit_name

    # noinspection PyProtectedMember
    def manipulate_resolution_plan(self, owning_bit, plan):
        part_of_bit = plan.bit_by_name(self.__bit_name)
        late_fake_bit = self.__late_fake_bit(owning_bit, part_of_bit, plan)
        modified = False
        for dependency in plan.dependencies_for_bit(part_of_bit):
            if isinstance(dependency, krrez.api.internal.SimpleDependency) and (dependency.afterwards is True) and (krrez.flow.bit_loader.bit_name(late_fake_bit) not in dependency.all_bit_names): # TODO nicer?!
                plan.dependencies_for_bit(late_fake_bit).append(dependency)
                plan.dependencies_for_bit(part_of_bit).remove(dependency)
                modified = True

        for bittype in plan.all_bits():
            patch_dependency_needed = False
            for dependency in plan.dependencies_for_bit(bittype):
                if isinstance(dependency, krrez.api.internal.SimpleDependency) and (dependency.afterwards is False) and krrez.flow.bit_loader.bit_name(part_of_bit) in dependency.all_bit_names:
                    patch_dependency_needed = True
                    break

            if patch_dependency_needed:
                found_patch_dependency = False
                for dependency in plan.dependencies_for_bit(bittype):
                    if isinstance(dependency, krrez.api.internal.SimpleDependency) and (dependency.afterwards is False) and krrez.flow.bit_loader.bit_name(late_fake_bit) in dependency.all_bit_names:
                        found_patch_dependency = True
                        break

                if not found_patch_dependency:
                    plan.dependencies_for_bit(bittype).append(krrez.api.internal.SimpleDependency([f"optional:{krrez.flow.bit_loader.bit_name(late_fake_bit)}"]))
                    modified = True
        return modified

    # noinspection PyProtectedMember
    def __late_fake_bit(self, owning_bit, part_of_bit, plan):
        late_fake_bit_name = f"{krrez.flow.bit_loader.bit_name(part_of_bit)}.SPECIAL.finished.Bit"
        late_fake_bit = plan.bit_by_name(late_fake_bit_name)
        if not late_fake_bit:
            late_fake_bit = krrez.flow.bit_loader.bit_by_name(late_fake_bit_name)
            plan.dependencies_for_bit(part_of_bit).append(krrez.api.internal.SimpleDependency([late_fake_bit_name], afterwards=True))
            plan.add_bit(late_fake_bit)
        plan.dependencies_for_bit(owning_bit).append(krrez.api.internal.SimpleDependency([late_fake_bit_name], afterwards=True))
        return late_fake_bit


class _InstallBeforehandForTestBundle(krrez.api.internal.SimpleDependency):

    def __init__(self, bit_name: str, profile_name: str, testbundle_name: str):
        super().__init__([bit_name])
        self.__profile_name = profile_name
        self.__testbundle_name = testbundle_name

    @property
    def testbundle_name(self):
        return self.__testbundle_name

    @property
    def profile_name(self):
        return self.__profile_name

    def additional_needed_bits(self, cooling_down, plan):
        if cooling_down:
            if any((krrez.flow.bit_loader.bit_name(bittype) == f"{krrez.coding.ProfileTests.profile_test_name_to_bit_name(self.__profile_name)}.{self.__testbundle_name}Bit") for bittype in plan.all_bits()):
                return super().additional_needed_bits(cooling_down, plan)
        return []
