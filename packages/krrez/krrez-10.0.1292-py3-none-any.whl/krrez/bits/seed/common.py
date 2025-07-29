# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess
import typing as t

import krrez.api.internal
import krrez.bits.sys.config
import krrez.flow.runner
import krrez.seeding.api
import krrez.seeding.system

if t.TYPE_CHECKING:
    import krrez.bits.seed.steps.disks


class ConfirmationBit(krrez.api.Bit):

    _confirmation = krrez.api.ConfigValue().ask_for.choose(
        "Welcome to Krrez installation.\n\n"
        "The following steps will install Krrez on the machine that you have attached the installation medium to. This"
        " will erase all data on this machine!\n\n"
        "Are you sure you want to continue?", choices={"Yes": True, "No": False})

    _stopped = krrez.api.ConfigValue().ask_for.choose(
        "Krrez installation was aborted. Please unplug the installation medium and restart the machine.", choices=[])

    def __apply__(self):
        if not self._confirmation.value:
            _ = self._stopped.value


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):

    _disks: "krrez.bits.seed.steps.disks.Bit"
    __more_deps: krrez.api.Beforehand["krrez.bits.seed.steps.bootloader.Bit",
                                      "krrez.bits.seed.steps.disks.Bit",
                                      "krrez.bits.seed.steps.drivers.Bit",
                                      "krrez.bits.seed.steps.final_reboot.Bit",
                                      "krrez.bits.seed.steps.first_boot.Bit",
                                      "krrez.bits.seed.steps.hostname.Bit",
                                      "krrez.bits.seed.steps.indirect.Bit",
                                      "krrez.bits.seed.steps.keyboard.Bit",
                                      "krrez.bits.seed.steps.krrez_bits.Bit",
                                      "krrez.bits.seed.steps.locale.Bit",
                                      "krrez.bits.seed.steps.machine_architecture.Bit",
                                      "krrez.bits.seed.steps.networking.Bit",
                                      "krrez.bits.seed.steps.seed_user.Bit",
                                      "krrez.bits.seed.steps.system_mounts.Bit",
                                      "krrez.bits.seed.steps.timezone.Bit"]

    _in_target_temp_context_path = krrez.api.ConfigValue(type=krrez.api.Path)

    def __apply__(self):
        with self._in_target_temp_context_path as x:
            x.value = in_target_temp_context_path = self._fs("/krrez_seed")

        try:
            self.__execute_stage(krrez.seeding.api.Stage.PREPARE)
            self.__execute_stage(krrez.seeding.api.Stage.PREPARE_RAW)
            self.__execute_stage(krrez.seeding.api.Stage.BUILD_RAW)
            self.__execute_stage(krrez.seeding.api.Stage.PREPARE_SYSTEM)
            self.__execute_stage(krrez.seeding.api.Stage.BUILD_SYSTEM)
            in_host_temp_context_path = self._disks.target_path.value(in_target_temp_context_path)
            krrez.seeding.system.turn_into_krrez_system(self._disks.target_path.value)
            krrez.flow.create_blank_context(self._internals.session.context,
                                            blank_context_path=in_host_temp_context_path,
                                            inherit_config_values=True)
            self.__execute_stage(krrez.seeding.api.Stage.PREPARE_CHROOT)
            self.__execute_stage(krrez.seeding.api.Stage.CHROOT)
            in_host_temp_context_path.remove(not_exist_ok=True)
        finally:
            self.__execute_stage(krrez.seeding.api.Stage.ON_EXIT)
            for _ in range(3):
                subprocess.check_output(["sync"])

    def __execute_stage(self, stage: krrez.seeding.api.Stage) -> None:
        bit_names = self._disks.bit_names_for_stage(stage)
        temp_context = krrez.flow.create_blank_context(self._internals.session.context, inherit_config_values=True)
        try:
            with self._log.block.info(f"Applying seed steps for {stage.value} stage.") as log_block:
                with krrez.flow.runner.Engine().start(context=temp_context, log_block=log_block,
                                                      bit_names=bit_names) as inner_runner:
                    inner_runner.ensure_successful()

        finally:
            krrez.flow.create_blank_context(temp_context, blank_context_path=self._internals.session.context.path,
                                            inherit_config_values=True)


class OperatingSystem:

    def __init__(self, *, name: str):
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name
