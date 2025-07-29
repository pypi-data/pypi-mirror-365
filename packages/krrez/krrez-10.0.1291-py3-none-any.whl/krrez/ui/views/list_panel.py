# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui.models.list_panel


class ListPanel(klovve.ui.ComposedView[krrez.ui.models.list_panel.ListPanel]):

    def compose(self):
        return klovve.views.responsive.Dual(
            item_1=klovve.views.VerticalBox(
                items=[
                    klovve.views.List(
                        items=self.model.bind(two_way=False).items,
                        selected_items=self.model.bind.selected_items,
                        selected_item=self.model.bind.selected_item,
                        item_label_func=self.model.bind(two_way=False).item_label_func),
                    klovve.views.VerticalBox(
                        items=self.model.bind.list_actions)],
                horizontal_layout=klovve.ui.Layout(klovve.ui.Align.FILL),
                is_visible=self.model.bind.is_list_visible),
            item_2=klovve.views.Placeholder(
                body=self.model.bind(two_way=False).body,
                horizontal_layout=klovve.ui.Layout(klovve.ui.Align.FILL_EXPANDING)))
