# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve.variable

import krrez.ui.models.property_panel


class PropertyPanel(klovve.ui.ComposedView[krrez.ui.models.property_panel.PropertyPanel]):
    # TODO support for non-string properties

    def _(self):
        if not self.model:
            return
        sections = []
        with klovve.variable.no_dependency_tracking():
            values = self.model.values
        for property in self.model.properties:
            sections.append(form_section := klovve.views.Form.Section(
                label=property.name,
                body=klovve.views.TextField(text=values.get(property, ""))))
            klovve.effect.activate_effect(self.__refresh_values, (form_section.body, property), owner=form_section)
        return klovve.views.Form(sections=sections)
    form_ui: klovve.ui.View = klovve.ui.computed_property(_)

    def __refresh_values(self, text_field: klovve.views.TextField, property: "Property") -> None:
        _values = {**self.model.values, property: text_field.text}
        if self.model.values != _values:
            self.model.values = _values

    def compose(self):
        return klovve.views.Placeholder(body=self.bind.form_ui)
