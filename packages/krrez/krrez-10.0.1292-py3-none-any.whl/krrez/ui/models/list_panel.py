# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve


class ListPanel(klovve.model.Model):

    items: list[t.Any] = klovve.model.list_property()

    selected_items: list[t.Any] = klovve.model.list_property()

    selected_item: t.Any = klovve.model.property()

    body: klovve.ui.View|None = klovve.model.property()

    item_label_func: t.Callable[[t.Any], str] = klovve.model.property()

    list_actions: list[klovve.ui.View] = klovve.model.list_property()

    is_list_visible: bool = klovve.model.property(initial=True)
