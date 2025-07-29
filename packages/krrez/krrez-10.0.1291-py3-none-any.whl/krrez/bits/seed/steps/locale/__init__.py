# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _locale = krrez.seeding.api.ConfigValue(type=str)


class InTargetBit(Bit):

    def __apply__(self):
        short_locales = [x for x in self._locale.value.replace(",", " ").replace(";", " ").split(" ") if x]
        full_locales = [f"{x}.UTF-8" for x in short_locales]
        to_be_generated_locals = ", ".join([f"{x} UTF-8" for x in full_locales])

        self._packages.install("locales", aux={"debconf": [
            f"locales locales/locales_to_be_generated multiselect {to_be_generated_locals}",
            f"locales locales/default_environment_locale select {full_locales[0]}"
        ]})
        subprocess.check_call(["dpkg-reconfigure", "-f", "noninteractive", "locales"])

        with open("/etc/default/locale", "a") as f:
            f.write(f"\nLANGUAGE={short_locales[0]}\n")
