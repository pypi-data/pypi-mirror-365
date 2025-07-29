# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Bit graph implementation, primarily used with the :py:mod:`krrez.flow.graph.resolver`.
"""
import itertools
import typing as t

import hallyd

import krrez.api
import krrez.flow.bit_loader


class Node:
    """
    One node in a bit graph, holding one bit, and pointing to all nodes that are considered as prerequisite
    of this node.

    There is no separate class for an entire graph, but you consider its root node as the graph.

    Such a graph is usually the result of dependency resolution for a list of bits to be installed.
    You usually do not create it manually, but get the graph from :py:mod:`krrez.flow.graph.resolver`.

    The root node is the final node regarding the execution order, while the leaves are the ones that execution can
    start with.
    """

    def __init__(self, bit: t.Optional[type["krrez.api.Bit"]]):
        """
        :param bit: The Bit to hold.
        """
        super().__init__()
        self.__bit = bit
        self.__after = []

    @property
    def after(self) -> list["Node"]:
        """
        The (editable) list of nodes that need to applied before this one can get applied.
        """
        return self.__after

    def __to_json_dict__(self):
        nodes_data_dict: dict["Node", tuple[int, str]] = {}
        id_counter = hallyd.lang.Counter()

        def get_storable(node: Node):
            nonlocal nodes_data_dict, id_counter

            result = nodes_data_dict.get(node)
            if not result:
                result = nodes_data_dict[node] = (id_counter.next(),
                                                  krrez.flow.bit_loader.bit_name(node.bit) if node.bit else None)
            return result

        afters = []

        for xcf in self.all_descendants(including_self=True):
            for xcf_child in xcf.after:
                afters.append((get_storable(xcf)[0], get_storable(xcf_child)[0]))

        return {"nodes": list(nodes_data_dict.values()), "beforehand_tuples": afters}

    @classmethod
    def __from_json_dict__(cls, json_dict):
        nodes = json_dict["nodes"]
        beforehand_tuples = json_dict["beforehand_tuples"]
        storable_nodes_dict = {node_id: Node(krrez.flow.bit_loader.bit_by_name(bit_name) if bit_name else None)
                               for node_id, bit_name in nodes}
        for after1id, after2id in beforehand_tuples:
            storable_nodes_dict[after1id].after.append(storable_nodes_dict[after2id])
        return storable_nodes_dict[1]

    @property
    def bit(self) -> t.Optional[type["krrez.api.Bit"]]:
        """
        The bit associated to this node. :code:`None` for the root node.
        """
        return self.__bit

    def nodes_reachable_from(self, nodes: t.Iterable["Node"]) -> t.Iterable["Node"]:
        """
        All nodes in this graph that are directly reachable, assuming that some nodes are already reached.

        :param nodes: The nodes that are already reached.
        """
        all_next_nodes = set()
        for node_a in self.all_descendants(starting_from_node=False, including_self=True):
            if (len(node_a.after) == 0) and (node_a not in nodes):
                all_next_nodes.add(node_a)
            for node_b in nodes:
                if node_b in node_a.after and node_a not in nodes:
                    all_next_nodes.add(node_a)
        result = []
        for next_node in all_next_nodes:
            dependencies_met = True
            for next_after_node in next_node.after:
                if next_after_node not in nodes:
                    dependencies_met = False
                    break
            if dependencies_met:
                result.append(next_node)
        return result

    def all_descendants(self, *, starting_from_node: bool = True, including_self: bool = False) -> t.Iterable["Node"]:
        """
        All descendants of this node.

        :param starting_from_node: Whether to start iterating from this node (instead of iterating in
                                   earliest-reachable-first order).
        :param including_self: Whether to include this node as well (instead of, actually, just descendants).
        """
        result = (entry[1] for entry in self.__all_descendants__helper())
        if including_self:
            result = itertools.chain((self,), result)
        if not starting_from_node:
            result = reversed(list(result))
        return result

    def condense(self, *, exclude_if: t.Callable[["Node"], bool]) -> None:
        """
        Removes some nodes from the graph, connecting its after-nodes to the predecessors.

        :param exclude_if: Function that decides if a node is to be removed.
        """
        retry = True
        changed = True
        while retry:
            if not changed:
                raise GraphError("tried to exclude a node that is not allowed to be excluded")
            retry = False
            changed = False
            for node_a in self.all_descendants():
                if exclude_if(node_a):
                    retry = True
                    if len(node_a.after) == 0:
                        self.__remove_node(node_a)
                        changed = True

    def node_for_bit(self, bit: type["krrez.api.Bit"]) -> t.Optional["Node"]:
        """
        The node in this graph that is associated to a given Bit (or :code:`None` if not found).

        :param bit: The bit to find.
        """
        for node in self.all_descendants():
            if node.bit == bit:
                return node

    def __all_descendants__helper(self) -> list[tuple["Node", "Node"]]:
        queue = [self]
        seen_nodes = set()
        while queue:
            n = queue.pop(0)
            for nc in n.after:
                if nc not in seen_nodes:
                    yield n, nc
                    seen_nodes.add(nc)
                    queue.append(nc)

    def __remove_node(self, node: "Node") -> None:
        for node_a in self.all_descendants(including_self=True):
            if node in node_a.after:
                node_a.after.remove(node)
                for cnode in node.after:
                    if cnode not in node_a.after:
                        node_a.after.append(cnode)


class GraphError(RuntimeError):
    """
    An error in graph processing occurred.
    """
