# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Visualizing for :py:class:`krrez.flow.graph`.
"""
import colorsys
import hashlib
import random
import typing as t

import krrez.flow.bit_loader
import krrez.flow.graph


def try_dump_pygraphviz(node: krrez.flow.graph.Node, extra_data: dict[str, str]) -> t.Optional[bytes]:
    """
    An SVG image that visualizes the given graph (or :code:`None` if pygraphviz is not available).

    :param node: The graph to visualize.
    :param extra_data: A dictionary that keeps the current stage for each node.
    """
    try:
        import pygraphviz
    except ImportError:
        return None
    pygraphviz_graph = pygraphviz.AGraph(directed=True, bgcolor="transparent")
    __try_dump_pygraphviz__dive(pygraphviz_graph, node, set(), extra_data)
    pygraphviz_graph.layout("dot")
    return pygraphviz_graph.draw(format="svg")


def __try_dump_pygraphviz__dive(pygraphviz_graph, node: krrez.flow.graph.Node, seen: set[krrez.flow.graph.Node],
                                extra_data: dict[str, str]):
    if node in seen:
        return
    seen.add(node)
    for node_after in node.after:
        __try_dump_pygraphviz__dive(pygraphviz_graph, node_after, seen, extra_data)
        node_key, _ = __try_dump_pygraphviz__add_pygraphviz_node(pygraphviz_graph, node, extra_data)
        node_after_key, color = __try_dump_pygraphviz__add_pygraphviz_node(pygraphviz_graph, node_after, extra_data)
        pygraphviz_graph.add_edge(node_after_key, node_key, color=color.scaled_by(0.66).as_html, penwidth=4)


def __try_dump_pygraphviz__add_pygraphviz_node(pygraphviz_graph, node: krrez.flow.graph.Node,
                                               extra_data: dict[str, str]):
    key = str(id(node))
    if node.bit:
        label = _label(node)
        fill_color = _fill_color(node, extra_data)
        border_color = _border_color(node, extra_data)
        text_color = Color(0, 0, 0)
    else:
        label = "▞▞▞▞"
        fill_color = border_color = Color(0, 0, 0)
        text_color = Color(0.9, 0.9, 0.9)
    pygraphviz_graph.add_node(key, label=label, fillcolor=fill_color.as_html, color=border_color.as_html,
                              fontcolor=text_color.as_html, style="filled,rounded", shape="box", penwidth=5,
                              fontname="Helvetica")
    return key, fill_color


def _label(node: krrez.flow.graph.Node) -> str:
    """
    The label string for a node.

    :param node: The node.
    """
    result_lines = []
    remaining_bit_name = krrez.flow.bit_loader.bit_name(node.bit)
    TYPICAL_LINE_LENGTH = 20
    while remaining_bit_name:
        if len(remaining_bit_name) <= TYPICAL_LINE_LENGTH:
            result_lines.append(remaining_bit_name)
            break

        for i in range(len(remaining_bit_name)):
            i_dot = remaining_bit_name[(i_search_offset := max(0, TYPICAL_LINE_LENGTH-i)):
                                       TYPICAL_LINE_LENGTH+i+1].find(".")
            if i_dot > 0:
                result_lines.append(remaining_bit_name[:i_dot+i_search_offset])
                remaining_bit_name = remaining_bit_name[i_dot+i_search_offset:]
                break
        else:
            result_lines.append(remaining_bit_name)
            break

    return "\n".join(result_lines)


def _border_color(node: krrez.flow.graph.Node, extra_data: dict[str, str]) -> "Color":
    """
    The border color for a node.

    :param node: The node.
    :param extra_data: Dictionary with state data per node.
    """
    hash_input = ".".join(krrez.flow.bit_loader.bit_name(node.bit).split(".")[:2])

    rnd = random.Random(int.from_bytes(hashlib.md5(hash_input.encode()).digest()[-5:], "big"))
    hue = rnd.uniform(0, 1)
    return Color(*colorsys.hsv_to_rgb(hue, 1, 0.5))


def _fill_color(node: krrez.flow.graph.Node, extra_data: dict[str, str]) -> "Color":
    """
    The fill color for a node.

    :param node: The node.
    :param extra_data: Dictionary with state data per node.
    """
    state_data = extra_data.get(krrez.flow.bit_loader.bit_name(node.bit))
    if state_data == "f":
        return Color(0.7, 0.4, 0.4)
    if state_data == "i":
        return Color(0.4, 0.4, 0.7)
    if state_data == "s":
        return Color(0.4, 0.7, 0.4)
    return Color(0.5, 0.5, 0.5)


class Color:
    """
    A color.
    """

    def __init__(self, red: float, green: float, blue: float):
        """
        :param red: The red component between 0 and 1.
        :param green: The green component between 0 and 1.
        :param blue: The blue component between 0 and 1.
        """
        self.__red = self.__trim_value(red)
        self.__green = self.__trim_value(green)
        self.__blue = self.__trim_value(blue)

    @staticmethod
    def __trim_value(value: float) -> float:
        """
        The original value trimmed to the interval 0..1.

        :param value: The value to trim.
        """
        return min(max(0.0, value), 1.0)

    @property
    def red(self) -> float:
        """
        The red component between 0 and 1.
        """
        return self.__red

    @property
    def green(self) -> float:
        """
        The green component between 0 and 1.
        """
        return self.__green

    @property
    def blue(self) -> float:
        """
        The blue component between 0 and 1.
        """
        return self.__blue

    @property
    def as_html(self) -> str:
        """
        The html color representation of this color.
        """
        return "#" + "".join([f"{int(value * 255):02x}" for value in (self.red, self.green, self.blue)])

    def scaled_by(self, factor: float) -> "Color":
        """
        A variant of this color, scaled by a given factor.

        :param factor: The factor. Lower than 1 makes it darker, higher than 1 makes it brighter.
        """
        return Color(self.red * factor, self.green * factor, self.blue * factor)
