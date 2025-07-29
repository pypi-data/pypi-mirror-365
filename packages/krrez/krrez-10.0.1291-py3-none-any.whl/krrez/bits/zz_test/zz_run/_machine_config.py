# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import contextlib
import importlib
import inspect
import typing as t

import krrez.api
import krrez.bits.seed.steps.networking


class _MachineConfiguration:

    def __init__(self, machine_short_name: str, profile_type_name: t.Optional[tuple[str, str]] = None,
                 profile_arguments: t.Optional[dict] = None, additional_config: t.Optional[dict] = None,
                 disk_sizes_gb: t.Iterable[float] = (45, 45), memory_gb: float = 4):  # TODO smaller
        self.__machine_short_name = machine_short_name
        self.profile_type_name = profile_type_name
        self.profile_arguments = {"hostname": f"x-{machine_short_name}.krz"} \
            if (profile_arguments is None) else profile_arguments
        self.additional_config = {
            **(additional_config or {}),
            "krrez.is_test_run": True,
            "seed.common.confirmation": "Yes"}
        self.disk_sizes_gb = disk_sizes_gb
        self.memory_gb = memory_gb

    @property
    def profile_type(self) -> t.Optional[type[krrez.api.Profile]]:
        if self.profile_type_name:
            return eval(self.profile_type_name[1], importlib.import_module(self.profile_type_name[0]).__dict__)

    @profile_type.setter
    def profile_type(self, value):
        self.profile_type_name = (value.__module__, value.__qualname__) if value else None

    @property
    def machine_short_name(self) -> str:
        return self.__machine_short_name


class _MachinesConfiguration:

    def __init__(self, machine_configurations: t.Optional[dict[str, "_MachineConfiguration"]] = None):
        self.__machine_configurations = machine_configurations or {}

    def machine_configuration(self, machine_short_name: str) -> "_MachineConfiguration":
        if machine_short_name not in self.__machine_configurations:
            self.__machine_configurations[machine_short_name] = _MachineConfiguration(machine_short_name)
        return self.__machine_configurations[machine_short_name]

    @property
    def machine_configurations(self) -> dict[str, "_MachineConfiguration"]:
        return self.__machine_configurations


@contextlib.contextmanager
def machine_configuration(run: "krrez.bits.zz_test.zz_run.Bit", machine_short_name: str, *,
                          store_afterwards: bool = True) -> t.Generator["_MachineConfiguration", None, None]:
    with run._internals.session.context.lock("machine_configuration", ns=_MachinesConfiguration):
        config = run.data("machine_configuration", None) or _MachinesConfiguration()
        yield config.machine_configuration(machine_short_name)
        if store_afterwards:
            run.set_data("machine_configuration", config)


def profile_for_machine(run: "krrez.bits.zz_test.zz_run.Bit", machine_short_name: str) -> krrez.api.Profile:
    with machine_configuration(run, machine_short_name, store_afterwards=False) as machine_config:
        pass
    kwargs, _ = _profile_arguments(dict(machine_config.profile_arguments), machine_config.profile_type)
    profile = machine_config.profile_type.get(kwargs)
    patch_profile_for_machine(machine_config.profile_type, machine_config.profile_arguments,
                              machine_config.additional_config, profile)
    return profile


def patch_profile_for_machine(profile_type, profile_arguments, additional_config, profile: krrez.api.Profile) -> None:
    _, profile_attrs = _profile_arguments(dict(profile_arguments), profile_type)

    if len(profile.network_interfaces) > 0 and len(profile.network_interfaces[0].connections) > 0:
        profile.network_interfaces[0].connections.clear()
        profile.network_interfaces[0].connections.append(krrez.bits.seed.steps.networking.ConnectIp4ByDHCP())

    profile.seed_user.password = "seed"

    for key in ["krrez_bits", "stage1_krrez_bits"]:
        setattr(profile, key, [*getattr(profile, key, ()), "zz_test.zz_run.exec_proxy", "zz_test.zz_run.no_raid_sync"])

    for key, value in profile_attrs.items():
        setattr(profile, key, value)

    for key, value in additional_config.items():
        profile.config[key] = value


def _profile_arguments(data: dict, profile_type) -> tuple[dict, dict]:
    data = dict(data)
    kwargs = {}
    for param in inspect.signature(profile_type).parameters.values():
        if param.name in data:
            kwargs[param.name] = data.pop(param.name)
    return kwargs, data
