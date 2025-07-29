# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Finding and loading bits.
"""
import functools
import logging
import importlib.util
import pkgutil
import re
import traceback
import typing as t

import hallyd

import krrez.api
import krrez.coding
import krrez.flow

if t.TYPE_CHECKING:
    import krrez.flow.config
    import krrez.flow.dialog
    import krrez.flow.writer


_logger = logging.getLogger(__name__)


def all_bits(*, accept_cached: bool = False) -> t.Iterable[type["krrez.api.Bit"]]:
    """
    All bits.

    See also :py:func:`all_normal_bits`.
    """
    return sorted(_all_bits(accept_cached=accept_cached), key=bit_name)


def all_normal_bits() -> t.Iterable[type["krrez.api.Bit"]]:
    """
    All normal bits.

    Excludes stuff like tests. See also :py:func:`all_bits`.
    """
    bits = []
    for bit in all_bits():
        if krrez.coding.Bits.is_bit_name_for_normal_bit(bit_name(bit)):
            bits.append(bit)
    return bits


def bit_by_name(name: str, all_bits: t.Optional[t.Iterable[type["krrez.api.Bit"]]] = None) -> type["krrez.api.Bit"]:
    """
    A bit by name. Raises :py:class:`BitNotFoundError` if not found.

    If the name contains '`.SPECIAL.`', it returns a special no-op bit. You usually do not need that; it is solely used
    internally.

    :param name: The bit name.
    """
    if "SPECIAL" in name.split("."):
        find_bit_module_name = name
        find_bit_type_name = "Bit"
        if find_bit_module_name.endswith("Bit"):
            find_bit_module_name, _, find_bit_type_name = find_bit_module_name.rpartition(".")
        exec_globals = dict(**globals())
        exec(f"class {find_bit_type_name}(krrez.api.Bit):\n"
             f"    def __apply__(self): pass\n"
             f"    __module__ = f'{krrez.flow.BITS_NAMESPACE}.{find_bit_module_name}'\n", exec_globals)
        # noinspection PyTypeChecker
        return exec_globals[find_bit_type_name]

    find_bit_full_name = bit_full_name(name)

    for bit in (all_bits or _all_bits()):
        if bit_full_name(bit) == find_bit_full_name:
            return bit

    raise BitNotFoundError(name)


def bit_name(bit: t.Union[str, "krrez.api.Bit", type["krrez.api.Bit"]]) -> str:
    """
    The (short) name of a bit.

    It is a substring of the type's full name: The prefix ":code:`krrez.bits.`" is removed, and if the class name equals
    to ":code:`Bit`", the ":code:`.Bit`" postfix is removed as well.

    See also :py:meth:`bit_full_name`.

    :param bit: The bit. Can be a short or long name, a type or an instance.
    """
    module_short_name, _, type_name = bit_full_name(bit)[len(krrez.flow.BITS_NAMESPACE)+1:].rpartition(".")
    return module_short_name if (type_name == "Bit") else f"{module_short_name}.{type_name}"


def bit_full_name(bit: t.Union[str, "krrez.api.Bit", type["krrez.api.Bit"]]) -> str:
    """
    The full name of a bit (equivalent to the type's full name incl. module name).

    See also :py:meth:`bit_name`.

    :param bit: The bit. Can be a short or long name, a type or an instance.
    """
    if isinstance(bit, krrez.api.Bit):
        bit = type(bit)

    if isinstance(bit, type) and issubclass(bit, krrez.api.Bit):
        bit = f"{bit.__module__}.{bit.__name__}"

    if not isinstance(bit, str):
        raise ValueError(f"invalid bit: {bit}")

    if not bit.startswith(f"{krrez.flow.BITS_NAMESPACE}."):
        bit = f"{krrez.flow.BITS_NAMESPACE}.{bit}"

    if not bit.endswith("Bit"):
        bit = f"{bit}.Bit"

    return bit


def bit_module_path(bit: t.Union["krrez.api.Bit", type["krrez.api.Bit"]]) -> hallyd.fs.Path:
    """
    The path of the Python module that contains this bit.
    """
    if not isinstance(bit, type):
        bit = type(bit)
    return hallyd.fs.Path(importlib.import_module(bit.__module__).__file__)


def bit_documentation(bit: t.Union["krrez.api.Bit", type["krrez.api.Bit"]]) -> str:
    """
    The documentation text of this bit.
    """
    if not isinstance(bit, type):
        bit = type(bit)
    return bit.__doc__ or ""


def bit_for_secondary_usage(bit_type: type["krrez.api.Bit"], *,
                            used_by: t.Optional["krrez.api.Bit"]) -> "krrez.api.Bit":
    """
    A bit by bit type, for secondary usage, i.e. not for calling its apply method.

    :param bit_type: The bit type to instantiate.
    :param used_by: The bit that currently runs its apply method (or None).
                    See :py:attr:`krrez.api.Bit._internals.origin_bit`.
    """
    base_bit = bit_type()
    base_bit._internals.initialize_as_secondary(used_by)
    return base_bit


@functools.lru_cache()
def _krrez_module_directories__helper(with_builtin: bool) -> list[hallyd.fs.Path]:
    result = []
    builtin_path = krrez.flow.KRREZ_SRC_ROOT_DIR.parent
    for bit in _all_bits():
        mpath = module_path = bit_module_path(bit)
        while mpath.name != "krrez":
            if mpath == mpath.parent:
                raise RuntimeError(f"the Bit module '{module_path}' seems to be in an invalid directory"
                                   f" structure; there should be a 'krrez' directory some levels above it")
            mpath = mpath.parent
        mpath = mpath.resolve().parent
        if mpath not in result and (with_builtin or mpath != builtin_path):
            result.append(mpath)
    result.sort()
    return result


def krrez_module_directories(*, with_builtin: bool) -> list[hallyd.fs.Path]:
    """
    All Krrez module root directories.

    :param with_builtin: Whether to include the builtin one as well.
    """
    return _krrez_module_directories__helper(bool(with_builtin))


def _join_package_name(*name_segments: t.Optional[str]) -> str:
    """
    Join package names, e.g. :code:`"foo"` and :code:`"bar.baz"` to :code:`"foo.bar.baz"`.

    :param name_segments: The name segments to join.
    """
    return ".".join(filter(None, name_segments))


def _is_valid_bit_name_segment(name_segment: str) -> bool:
    """
    Whether a string is a valid name segment.

    :param name_segment: The name segment to check.
    """
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name_segment) is not None


_all_bits_cache = None


def _all_bits(*, accept_cached: bool = False) -> t.Iterable[type["krrez.api.Bit"]]:
    global _all_bits_cache
    if not accept_cached or _all_bits_cache is None:
        _all_bits_cache = tuple(_all_bits__helper(None))
    return _all_bits_cache


def _all_bits__helper(sub_package_name: t.Optional[str]) -> t.Iterable[type["krrez.api.Bit"]]:
    spec = importlib.util.find_spec(_join_package_name(krrez.flow.BITS_NAMESPACE, sub_package_name))
    if spec.submodule_search_locations:
        seen_child_names = set()
        for child_module in pkgutil.iter_modules(spec.submodule_search_locations):
            if not _is_valid_bit_name_segment(child_module.name):
                continue
            seen_child_names.add(child_module.name)
            child_module_name = _join_package_name(sub_package_name, child_module.name)
            try:
                module = importlib.import_module(_join_package_name(krrez.flow.BITS_NAMESPACE, child_module_name))
                for bit_tuple in _all_bits__helper__deep(module.__name__, child_module_name):
                    yield bit_tuple
            except ModuleNotFoundError:
                pass
            except Exception:
                _logger.debug(traceback.format_exc())
        for sub_path in map(hallyd.fs.Path, spec.submodule_search_locations):
            if not _is_valid_bit_name_segment(sub_path.name):
                continue
            for sub_sub_path in sub_path.iterdir():
                if not _is_valid_bit_name_segment(sub_sub_path.name):
                    continue
                if (sub_sub_path.name not in seen_child_names) and sub_sub_path.is_dir():
                    seen_child_names.add(sub_sub_path.name)
                    for bit_tuple in _all_bits__helper__deep(
                            None, _join_package_name(sub_package_name, sub_sub_path.name)):
                        yield bit_tuple


def _all_bits__helper__deep(module_name, sub_package_name) -> t.Iterable[type["krrez.api.Bit"]]:
    if module_name:
        modl = importlib.import_module(module_name)
        for typ in [t for t in [getattr(modl, itm) for itm in dir(modl) if itm.endswith("Bit")]
                    if isinstance(t, type) and issubclass(t, krrez.api.Bit)]:
            yield typ
    for crpn in _all_bits__helper(sub_package_name):
        yield crpn


class BitNotFoundError(RuntimeError):
    """
    A bit was tried to access that does not seem to exist.
    """

    def __init__(self, bit_name: str):
        super().__init__(f"bit not found: {bit_name}")
