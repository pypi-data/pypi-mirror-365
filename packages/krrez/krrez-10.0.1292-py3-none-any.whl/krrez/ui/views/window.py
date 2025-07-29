# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve.driver


class Window(klovve.views.Window):

    def __init__(self, **kwargs):
        layout_provider = Window._LayoutProvider()
        super().__init__(**kwargs,
                         horizontal_layout=layout_provider.bind.layout,
                         vertical_layout=layout_provider.bind.layout)

    class _LayoutProvider(klovve.model.Model):

        async def _(self):
            is_terminal = klovve.driver.Driver.get().name() == "viwid"
            align = klovve.ui.Align.FILL_EXPANDING if is_terminal else klovve.ui.Align.FILL
            return klovve.ui.Layout(align)
        layout = klovve.model.computed_property(_, async_initial=lambda: klovve.ui.Layout(klovve.ui.Align.FILL))
