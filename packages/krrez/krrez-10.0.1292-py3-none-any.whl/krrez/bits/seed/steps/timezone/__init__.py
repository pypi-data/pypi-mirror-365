# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _timezone = krrez.seeding.api.ConfigValue(type=str)


class InTargetBit(Bit):

    def __apply__(self):
        self._fs("/etc/localtime").unlink()
        self._fs("/etc/localtime").symlink_to(f"/usr/share/zoneinfo/{self._timezone.value}")

        subprocess.check_call(["dpkg-reconfigure", "-f", "noninteractive", "tzdata"])
