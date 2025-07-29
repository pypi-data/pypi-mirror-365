# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import krrez.bits.seed.steps.disks
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _disks: krrez.bits.seed.steps.disks.Bit


class InHostPrepareChrootBit(Bit):

    def __apply__(self):
        # https://serverfault.com/questions/1079653
        for bind_path in ["/proc", "/dev", "/dev/pts", "/sys"]:
            with self._disks.umounts as x:
                x.value.append(bind_path)

            options = {
                "/dev": ("-t", "devtmpfs", "udev"),
                "/dev/pts": ("-t", "devpts", "devpts"),
                "/proc": ("-t", "proc", "proc"),
            }.get(bind_path, ("--bind", bind_path))

            subprocess.check_call(["mount", *options, str(self._disks.target_path.value) + bind_path])
