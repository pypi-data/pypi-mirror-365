# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t
import klovve

import krrez.ui.apps.dev_lab.models.main


class BitEditor(klovve.model.Model):

    bit: "krrez.ui.apps.dev_lab.models.main.Bit|None" = klovve.model.property()

    def _(self):
        return f"Bit {self.bit.name!r}" if self.bit else ""
    header_text: str = klovve.model.computed_property(_)

    def _(self):
        return str(self.bit.module_path) if self.bit else ""
    module_path_text: str = klovve.model.computed_property(_)

    def handle_remove_bit(self, bit: "krrez.ui.apps.dev_lab.models.main.Bit") -> None:
        self.trigger_event(krrez.ui.apps.dev_lab.models.main.RemoveBitEvent(bit))
