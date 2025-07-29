# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve


class NewTestRun(klovve.model.Model):

    all_test_plans: list[str] = klovve.model.list_property()

    selected_test_plan: str|None = klovve.model.property()

    def _(self):
        return bool(self.selected_test_plan)
    is_form_valid: bool = klovve.model.computed_property(_)
