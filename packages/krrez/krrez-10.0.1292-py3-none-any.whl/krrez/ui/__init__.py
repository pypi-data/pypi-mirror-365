# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve.driver

import krrez.api
import krrez.flow.bit_loader


class RuntimeData(klovve.model.Model):

    context: krrez.flow.Context = klovve.model.property()

    all_bits: list[type[krrez.api.Bit]] = klovve.model.list_property()


class Application(klovve.app.Application):

    driver_compatibility = klovve.app.Application._CompatibilitySpecification(level=klovve.driver.Driver.LEVEL_TERMINAL)

    runtime_data: RuntimeData = klovve.model.property()

    @klovve.timer.run_timed(interval=60)
    def __refresh_all_bits(self):
        self.runtime_data.all_bits = krrez.flow.bit_loader.all_bits()
