# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import hallyd

import krrez.bits.sys.next_boot
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _next_boot: krrez.bits.sys.next_boot.Bit

    _first_boot_actions = krrez.seeding.api.ConfigValue(default=[], type=list[hallyd.services.TRunnable])


class InTargetBit(Bit):

    def __apply__(self):
        for action in self._first_boot_actions.value:
            with self._next_boot.create_task(None, action) as _:
                _.run_interactively()
                _.add_dependency("krz_seed_apply_bits")
                _.add_dependency("krz_seed_final_reboot", afterwards=True)
