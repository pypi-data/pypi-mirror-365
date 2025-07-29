# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve


class SessionInteraction(klovve.model.Model):

    method_name: str|None = klovve.model.property()

    args: list[object] = klovve.model.property(initial=lambda: [])

    kwargs: dict[str, object] = klovve.model.property(initial=lambda: {})

    answer: object = klovve.model.property()
