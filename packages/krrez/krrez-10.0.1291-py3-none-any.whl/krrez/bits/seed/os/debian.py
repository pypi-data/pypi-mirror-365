# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import krrez.api
import krrez.bits.seed.common


class Bit(krrez.api.Bit):

    __more_deps: krrez.api.Beforehand["krrez.bits.seed.steps.debootstrap.Bit"]
    __later: krrez.api.Later["krrez.bits.seed.common.Bit"]


class OperatingSystem(krrez.bits.seed.common.OperatingSystem):

    def __init__(self, version_name: str):
        super().__init__(name="debian")
        self.version_name = version_name
