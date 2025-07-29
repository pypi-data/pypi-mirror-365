# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import hallyd

import krrez.bits.seed.steps.bootloader
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _bootloader: krrez.bits.seed.steps.bootloader.Bit

    _indirect__void_installation_medium_during_seed = krrez.seeding.api.ConfigValue(default=False, type=bool)


class InHostPrepareBit(Bit):

    def __apply__(self):
        if self._indirect__void_installation_medium_during_seed.value:
            if self._bootloader.bootloader == "efi":
                hallyd.fs.Path("/boot/efi").remove(on_error=hallyd.fs.OnRemoveError.SKIP_AND_IGNORE,
                                                   on_passing_filesystem_boundary=hallyd.fs.OnRemovePassingFileSystemBoundary.CONTINUE_REMOVING_BEHIND_BOUNDARY)

            else:
                raise ValueError(f"bootloader {self._bootloader.bootloader!r} unsupported")
