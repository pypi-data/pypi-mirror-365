# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import krrez.bits.sys.next_boot
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):
    pass


class InTargetBit(Bit):

    _next_boot: krrez.bits.sys.next_boot.Bit

    def __apply__(self):
        with self._next_boot.create_task("krz_seed_final_reboot", _reboot) as _:
            _.add_dependency("krz_seed_apply_bits")


def _reboot(run):
    run.reboot()
