# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Main programming interface for the implementation of seeding bits.
"""
import enum
import importlib
import typing as t

import krrez.api.internal
import krrez.flow.config


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):

    def bit_names_for_stage(self, stage: "Stage") -> list[str]:
        return self._internals.session.context.config.get(_BIT_NAMES_CONFIG_KEY)[_key_name_for_stage(stage)]

    def __apply__(self):
        if type(self).__name__ == "Bit":
            self_module = importlib.import_module(type(self).__module__)
            for item_name in dir(self_module):
                item = getattr(self_module, item_name)
                if isinstance(item, type) and issubclass(item, Bit):
                    if item_name.endswith("Bit") and item_name != "Bit":
                        bit_stage_name = item_name[:-len("Bit")]
                        for stage in Stage:
                            if stage.value.replace("_", "").lower() == bit_stage_name.lower():
                                config = self._internals.session.context.config

                                stage_bit_names = config.get(_BIT_NAMES_CONFIG_KEY, {})
                                stage_config_key = _key_name_for_stage(stage)
                                stage_bit_names[stage_config_key] = bits = stage_bit_names.get(stage_config_key, [])

                                bits.append(f"{self.name}.{item_name}")
                                config.set(_BIT_NAMES_CONFIG_KEY, stage_bit_names)
                                break


class Stage(enum.Enum):
    PREPARE = "in_host_prepare"
    PREPARE_RAW = "in_host_prepare_raw"
    BUILD_RAW = "in_host_build_raw"
    PREPARE_SYSTEM = "in_host_prepare_system"
    BUILD_SYSTEM = "in_host_build_system"
    PREPARE_CHROOT = "in_host_prepare_chroot"
    CHROOT = "in_host_chroot"
    IN_TARGET = "in_target"
    IN_TARGET_LATE = "in_target_late"
    ON_EXIT = "in_host_on_exit"


_TConfigValueType = t.TypeVar("_TConfigValueType")


class ConfigValue(krrez.api.internal.BareConfigValue[_TConfigValueType], t.Generic[_TConfigValueType]):

    def __init__(self, *, default=None, type: type[_TConfigValueType] = object):
        super().__init__(module_name="seed", default=default, type=type)


def _key_name_for_stage(stage: Stage) -> str:
    return f"seed.{stage.value}_bits"


_BIT_NAMES_CONFIG_KEY = "seed.bit_names_for_stage"
