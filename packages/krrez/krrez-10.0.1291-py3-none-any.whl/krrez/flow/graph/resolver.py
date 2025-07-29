# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Dependency resolution for bits.
"""
import abc
import typing as t

import krrez.api.internal
import krrez.coding
import krrez.flow.bit_loader
import krrez.flow.graph


def graph_for_bits(bits: t.Iterable[type["krrez.api.Bit"]]) -> "krrez.flow.graph.Node":
    """
    A graph of bits, containing the given bits and their dependencies, connected in a valid way.

    :param bits: The bits that the graph at least have to contain.
    """
    plan = _Plan()
    for bit in bits:
        plan.add_bit(bit)
    _expand_by_dependencies_and_list_manipulations(plan)

    root_node = krrez.flow.graph.Node(None)
    for bit in sorted(plan.all_bits(), key=krrez.flow.bit_loader.bit_name):
        root_node.after.append(krrez.flow.graph.Node(bit))

    _fill_dependencies_to_nodes(root_node, plan)
    _cleanup_dependencies_from_nodes(root_node)

    return root_node


def _expand_by_dependencies_and_list_manipulations(plan: "Plan") -> None:
    """
    Expand a plan by dynamical mechanisms, in order to refine the plan.

    :param plan: The plan to adapt.
    """
    hot = True
    cooling_down = True
    all_bits = krrez.flow.bit_loader.all_bits()
    while hot:
        if cooling_down:
            hot = False
        cooling_down = True

        for bit in tuple(plan.all_bits()):
            other_bit_names = set()
            for dependency in plan.dependencies_for_bit(bit):
                other_bit_names.update(dependency.additional_needed_bits(cooling_down, plan))
            for other_bit_name in other_bit_names:
                if other_bit_name not in [krrez.flow.bit_loader.bit_name(b) for b in plan.all_bits()]:
                    plan.add_bit(krrez.flow.bit_loader.bit_by_name(other_bit_name, all_bits))
                    cooling_down = False

            for dependency in plan.dependencies_for_bit(bit):
                if dependency.manipulate_resolution_plan(bit, plan):
                    cooling_down = False

        if not cooling_down:
            hot = True


def _fill_dependencies_to_nodes(root_node: "krrez.flow.graph.Node", plan: "Plan") -> None:
    """
    Transfer the dependencies from a plan into a graph.

    :param root_node: The graph to adapt.
    :param plan: The plan to take the dependencies from.
    """
    for n1 in root_node.all_descendants():
        for n2 in root_node.all_descendants():
            if n1 == n2:
                continue
            n1_may_be_installed_before_n2 = _may_be_installed_before(n1.bit, n2.bit, plan)
            n2_may_be_installed_before_n1 = _may_be_installed_before(n2.bit, n1.bit, plan)
            if n1_may_be_installed_before_n2 and not n2_may_be_installed_before_n1:
                n2.after.append(n1)
            elif not n1_may_be_installed_before_n2 and not n2_may_be_installed_before_n1:
                raise DependenciesCannotBeMetError(f"there is no valid order for"
                                                   f" '{krrez.flow.bit_loader.bit_name(n1.bit)}'"
                                                   f" and '{krrez.flow.bit_loader.bit_name(n2.bit)}'")


class Plan(abc.ABC):
    """
    Data structure for dependency resolution, keeping all required bits and their dependencies.

    This is turned into a graph after dependency resolution has finished.
    """

    @abc.abstractmethod
    def add_bit(self, bit: type["krrez.api.Bit"]) -> None:
        """
        Adds a bit, so make it part of the later graph.

        :param bit: The Bit to add.
        """

    @abc.abstractmethod
    def bit_by_name(self, bit_name: str) -> t.Optional[type["krrez.api.Bit"]]:
        """
        The bit by name (or :code:`None` if not found).

        :param bit_name: The bit name.
        """

    @abc.abstractmethod
    def all_bits(self) -> t.Iterable[type["krrez.api.Bit"]]:
        """
        All bits currently listed to become part of the later graph.
        """

    @abc.abstractmethod
    def dependencies_for_bit(self, bit: type["krrez.api.Bit"]) -> list["krrez.api.internal.Dependency"]:
        """
        The (editable) list of dependencies for a bit.

        :param bit: The bit.
        """


class _Plan(Plan):
    """
    :py:class:`Plan` implementation.
    """

    def __init__(self):
        self.__data = {}
        self.__dependencies_from_annotations__cache = {}
        self.__bits = {}
        self.__all_bits = None

    def add_bit(self, bit):
        self.__bits[krrez.flow.bit_loader.bit_name(bit)] = bit

    def bit_by_name(self, bit_name):
        bit_full_name = krrez.flow.bit_loader.bit_full_name(bit_name)
        for bit_name_, bit in self.__bits.items():
            if krrez.flow.bit_loader.bit_full_name(bit_name_) == bit_full_name:
                return bit

    def all_bits(self):
        return tuple([x for x in self.__bits.values()])

    def dependencies_for_bit(self, bit):
        bit_name = krrez.flow.bit_loader.bit_name(bit)

        if bit_name not in self.__data:
            self.__data[bit_name] = list(self.__dependencies_from_annotations(bit))
        return self.__data[bit_name]

    def __dependencies_from_annotations(self,
                                        bit: type["krrez.api.Bit"]) -> t.Iterable["krrez.api.internal.Dependency"]:
        bit_name = krrez.flow.bit_loader.bit_name(bit)
        if bit_name not in self.__dependencies_from_annotations__cache:
            result = []

            for my_type in reversed(bit.__mro__):
                for var_name, unresolved_foreign_bit_type in getattr(my_type, "__annotations__", {}).items():
                    if isinstance(unresolved_foreign_bit_type, krrez.api.internal.Dependency):
                        result.append(unresolved_foreign_bit_type)

            if not self.__all_bits:
                self.__all_bits = krrez.flow.bit_loader.all_bits()

            # noinspection PyProtectedMember
            for var_name, (foreign_bit_type, foreign_bit_gname, foreign_bit_origref
                           ) in bit._all_bit_usage_declarations(all_bits=self.__all_bits).items():
                derive_a_dependency = True
                if foreign_bit_type:
                    for ttype in foreign_bit_type.mro():
                        if getattr(ttype, "_krrez_do_not_derive_a_dependency", False):
                            derive_a_dependency = False
                            break
                if derive_a_dependency:
                    result.append(krrez.api.internal.SimpleDependency([foreign_bit_origref]))

            sys_config_needed = False
            for my_type in reversed(bit.__mro__):
                if sys_config_needed:
                    break
                for var_value in my_type.__dict__.values():
                    if isinstance(var_value, krrez.api.internal.BareConfigValue):
                        sys_config_needed = True
                        break
            if sys_config_needed:
                result.append(krrez.api.internal.SimpleDependency(["krrez.bits.sys.config.Bit"]))

            self.__dependencies_from_annotations__cache[bit_name] = tuple(result)
        return self.__dependencies_from_annotations__cache[bit_name]


def _may_be_installed_before(bit: type["krrez.api.Bit"],
                             other_bit: type["krrez.api.Bit"],
                             plan: Plan) -> bool:
    """
    Whether a bit can be installed before another bit, according to a plan.

    :param bit: The first bit.
    :param other_bit: The other bit.
    :param plan: The plan to consider.
    """
    for dependency in plan.dependencies_for_bit(bit):
        if dependency.relative_order(bit, other_bit) < 0:
            return False
    for dependency in plan.dependencies_for_bit(other_bit):
        if dependency.relative_order(other_bit, bit) > 0:
            return False
    return True


def _cleanup_dependencies_from_nodes(root_node: "krrez.flow.graph.Node") -> None:
    """
    Removes all dependencies from a graph that are redundant.

    :param root_node: The graph to clean-up.
    """
    for ry in root_node.all_descendants(including_self=True):
        for rx in list(ry.after):
            larger_exists = False
            for after_ry in ry.after:
                for node in after_ry.all_descendants():
                    if node == after_ry:
                        raise RuntimeError(f"unexpected graph circle around"
                                           f" {krrez.flow.bit_loader.bit_name(node.bit)}")
                    if node == rx:
                        larger_exists = True
                        break
            if larger_exists:
                ry.after.remove(rx)


class DependenciesCannotBeMetError(RuntimeError):
    """
    Error in realizing dependencies.
    """

    def __init__(self, details: str):
        super().__init__(f"Dependencies cannot be met: {details}")
