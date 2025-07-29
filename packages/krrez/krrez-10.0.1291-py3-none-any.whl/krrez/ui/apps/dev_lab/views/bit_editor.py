# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t
import klovve

import krrez.ui.apps.dev_lab.models.bit_editor
import krrez.ui.apps.dev_lab.models.main


class BitEditor(klovve.ui.ComposedView[krrez.ui.apps.dev_lab.models.bit_editor.BitEditor]):

    def compose(self):
        return klovve.views.Scrollable(
            body=klovve.views.Form(
                sections=[
                    klovve.views.Label(text=self.model.bind.header_text),
                    klovve.views.Form.Section(
                        label="If you want to make any changes to this Bit, modify its code in this file:",
                        body=klovve.views.Label(text=self.model.bind.module_path_text)),
                    klovve.views.Form.Section(
                        body=klovve.views.Button(text="Remove this Bit", action_name="remove_bit"))]))

    @klovve.event.action("remove_bit")
    async def __handle_remove_bit(self, event):
        if await self.application.dialog(klovve.views.interact.MessageYesNo(
                message=f"Do you really want to delete the Bit {self.bit.name!r}?"), view_anchor=event.triggering_view):
            self.model.handle_remove_bit(self.bit)
