# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import krrez.bits.seed.steps.disks
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _disks: "krrez.bits.seed.steps.disks.Bit"

    hostname = krrez.seeding.api.ConfigValue(type=str)

    @property
    def short_hostname(self):
        return self.hostname.value.split(".")[0]


class InHostPrepareSystemBit(Bit):

    def __apply__(self):
        self._disks.target_path.value("etc/hostname").write_text(self.short_hostname)


class InHostPrepareChrootBit(Bit):

    def __apply__(self):
        with open(self._disks.target_path.value("etc/hosts"), "a") as f:
            f.write(f"\n127.0.1.1 {self.hostname.value} {self.short_hostname}\n")


class InTargetBit(Bit):

    def __apply__(self):#TODO needed? or even earlier?! apply_in_target_early?!
        subprocess.check_call(["hostname", self.short_hostname])
