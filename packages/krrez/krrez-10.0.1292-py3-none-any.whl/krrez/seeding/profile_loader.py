# SPDX-FileCopyrightText: © 2024 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Finding and loading profiles.
"""
import importlib.util
import pkgutil
import typing as t

import hallyd

import krrez.api
import krrez.flow


def profile_module_path(profile: t.Union["krrez.api.Profile", type["krrez.api.Profile"]]) -> hallyd.fs.Path:
    """
    The path of the Python module that contains this profile.
    """
    if not isinstance(profile, type):
        profile = type(profile)
    return hallyd.fs.Path(importlib.import_module(profile.__module__).__file__)


def profile_name(profile: t.Union[str, "krrez.api.Profile", type["krrez.api.Profile"]]) -> str:
    """
    The (short) name of a profile.

    See also :py:meth:`profile_full_name`.

    :param profile: The profile. Can be a short or long name, a type or an instance.
    """
    module_short_name, _, type_name = profile_full_name(profile)[len(krrez.flow.PROFILES_NAMESPACE)+1:].rpartition(".")
    return module_short_name if (type_name == "Profile") else f"{module_short_name} {type_name}"


def profile_full_name(profile: t.Union[str, "krrez.api.Profile", type["krrez.api.Profile"]]) -> str:
    """
    The full name of a profile (equivalent to the type's full name incl. module name).

    See also :py:meth:`profile_name`.

    :param profile: The profile. Can be a short or long name, a type or an instance.
    """
    if isinstance(profile, krrez.api.Profile):
        profile = type(profile)

    if isinstance(profile, type) and issubclass(profile, krrez.api.Profile):
        profile = f"{profile.__module__}.{profile.__name__}"

    if not isinstance(profile, str):
        raise ValueError(f"invalid profile: {profile}")

    if profile.startswith(f"{krrez.flow.PROFILES_NAMESPACE}."):
        return profile

    name1, _, type_name = profile.rpartition(" ")
    return f"{krrez.flow.PROFILES_NAMESPACE}.{f'{name1}.{type_name}' if type_name else name1}"


def all_profiles() -> list[type["krrez.api.Profile"]]:
    """
    All profiles.

    This also includes internal hidden profiles. See also :py:func:`browsable_profiles`.
    """
    result = []

    for module in _modules():
        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, type) and issubclass(item, krrez.api.Profile):
                result.append(item)

    return result


def browsable_profiles() -> list[type["krrez.api.Profile"]]:
    """
    All browsable profiles.

    See also :py:func:`all_profiles`.
    """
    available_profiles = []

    for available_profile in all_profiles():
        if not (available_profile.is_browsable and not available_profile.is_hidden):
            continue

        can_handle_parameters = True
        for open_parameter in available_profile.open_parameters:
            if open_parameter.type is not str:
                can_handle_parameters = False
        if not can_handle_parameters:
            continue

        available_profiles.append(available_profile)

    return sorted(available_profiles, key=lambda profile: profile.name)


def _modules(modname=krrez.flow.PROFILES_NAMESPACE) -> list[t.Any]:
    # TODO
    module_names = set()

    def add_result(sub_module_name: str) -> None:
        nonlocal module_names
        module_names.add(f"{modname}.{sub_module_name}")
        module_names.update(_modules(f"{modname}.{sub_module_name}"))

    spec = importlib.util.find_spec(modname)

    if spec.submodule_search_locations:
        for search_location in spec.submodule_search_locations:
            for item in hallyd.fs.Path(search_location).iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    add_result(item.name)

        for sub_module in pkgutil.iter_modules(spec.submodule_search_locations):
            add_result(sub_module.name)

    return [importlib.import_module(module_name) for module_name in module_names]
