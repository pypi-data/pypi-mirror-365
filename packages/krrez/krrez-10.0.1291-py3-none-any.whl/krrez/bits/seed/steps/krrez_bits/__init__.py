# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import functools
import time
import traceback
import typing as t

import krrez.bits.sys.next_boot
import krrez.flow.runner
import krrez.flow.ui
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _next_boot: krrez.bits.sys.next_boot.Bit

    _krrez_bits = krrez.seeding.api.ConfigValue(default=[], type=list[str])
    _krrez_on_error_func = krrez.seeding.api.ConfigValue(type=t.Optional[t.Callable])
    _config = krrez.seeding.api.ConfigValue(default={}, type=dict)


class InTargetBit(Bit):

    def __apply__(self):
        std_context = krrez.flow.Context()
        for config_key, config_value in self._config.value.items():
            std_context.config.set(config_key, config_value)

        if self._krrez_bits.value:
            with self._next_boot.create_task("krz_seed_apply_bits",
                                             functools.partial(self._apply_bits, self._krrez_bits.value,
                                                               self._krrez_on_error_func.value)) as _:
                _.run_interactively()

        self._fs("/etc/systemd/system.conf.d").make_dir(exist_ok=True)("krrez_foo.conf").set_data(
            "[Manager]\nShowStatus = false\n", readable_by_all=True)

    @staticmethod
    def _apply_bits(krrez_bits, on_error_func):
        if krrez_bits:
            while True:
                do_retry = False
                try:
                    with krrez.flow.ui.app("runner", krrez.flow.Context().path, bit_names=krrez_bits,
                                           engine=krrez.flow.runner.Engine(),
                                           confirm_after_installation=False) as (app, app_ctrl):
                        app_ctrl.run()
                        if not app.was_successful:
                            raise RuntimeError("applying of bits failed")

                    time.sleep(20)  # TODO for finish_from_here; do better
                    break

                except Exception:

                    if on_error_func:
                        try:
                            on_error_func()
                        except Retry:
                            do_retry = True

                    if do_retry:
                        traceback.print_exc()
                        print("\nSomething failed; retrying later...")  # TODO more text

                        time.sleep(10.4)  # TODO nicer, longer
                        continue

                    traceback.print_exc()
                    print("\nThe process stopped immaturely due to a fatal error.")  # TODO more text (and auto reboot after some time?); dedup
                    while True:
                        time.sleep(1000)


class Retry(BaseException):
    pass
