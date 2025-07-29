# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import dataclasses
import typing as t

import klovve


class PropertyPanel(klovve.model.Model):

    @dataclasses.dataclass(frozen=True)
    class Property:
        name: str
        type: type[t.Any]

    properties: list[Property] = klovve.ui.list_property()

    values: dict[Property, t.Any] = klovve.ui.property(initial=lambda: {})
