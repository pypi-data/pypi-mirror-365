# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import hallyd

import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    drivers = krrez.seeding.api.ConfigValue(default=[], type=list[str])


class InTargetBit(Bit):

    def __apply__(self):
        drivers = [_ for _
                    in (self.drivers.value.split(" ") if isinstance(self.drivers.value, str) else self.drivers.value)
                    if _]

        if drivers:
            _enable_apt_contrib_non_free()
            self._packages.install(*drivers)


def _enable_apt_contrib_non_free():
    sources_list_file = hallyd.fs.Path("/etc/apt/sources.list")
    new_sources_list_content = ""
    for sources_list_line in sources_list_file.read_text().strip().split("\n"):
        if sources_list_line.endswith(" main"):
            for archive_area in ["contrib", "non-free", "non-free-firmware"]:
                if f" {archive_area} " not in sources_list_line:
                    sources_list_line = f"{sources_list_line[:-5]} {archive_area}{sources_list_line[-5:]}"
        new_sources_list_content += sources_list_line + "\n"
    sources_list_file.set_data(new_sources_list_content)

    subprocess.check_call(["apt-get", "update"])
