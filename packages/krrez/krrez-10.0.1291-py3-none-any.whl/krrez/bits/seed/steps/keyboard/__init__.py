# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _keyboard = krrez.seeding.api.ConfigValue(type="Keyboard")


class InTargetBit(Bit):

    def __apply__(self):
        keyboard = self._keyboard.value

        self._packages.install("keyboard-configuration", aux={"debconf": [
            f"keyboard-configuration keyboard-configuration/modelcode string {keyboard.model}",
            f"keyboard-configuration keyboard-configuration/xkb-keymap select {keyboard.layout}",
            f"keyboard-configuration keyboard-configuration/variantcode string {keyboard.variant}"
        ]})
        subprocess.check_call(["dpkg-reconfigure", "-f", "noninteractive", "keyboard-configuration"])

        self._packages.install("console-setup")


class Keyboard:
    """
    A keyboard specification as used in KeyboardSettingSpec.
    """

    def __init__(self, *, layout: str, variant: str = "", model: str = "pc105"):
        """
        :param layout: Keyboard layout, like `"us"` or `"de"`.
        :param variant: Optional keyboard variant, like `"nodeadkeys"` or `"mac"`.
        :param model: Optional keyboard model, like `"pc105"`.
        """
        self.layout = layout
        self.variant = variant
        self.model = model
