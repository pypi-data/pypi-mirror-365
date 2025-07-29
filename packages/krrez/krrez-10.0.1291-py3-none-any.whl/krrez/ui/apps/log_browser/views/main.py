# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow
import krrez.ui.models.list_panel
import krrez.ui.views.list_panel
import krrez.ui.views.session
import krrez.ui.models.session
import krrez.ui.apps.log_browser.models.main


class Main(klovve.ui.ComposedView[krrez.ui.apps.log_browser.models.main.Main]):

    def compose(self):
        if len(self.model.all_sessions) == 0:
            return klovve.views.Label(text="You have not installed any Krrez bits yet.")

        else:
            return krrez.ui.views.list_panel.ListPanel(
                model=krrez.ui.models.list_panel.ListPanel(
                    items=self.model.bind.all_sessions,
                    item_label_func=(lambda item: item.name),
                    selected_item=self.model.bind.selected_session,
                    body=self.bind.view_for_panel))

    def _(self):
        if not self.model:
            return None
        if self.model.selected_session:
            return krrez.ui.views.session.Session(model=krrez.ui.models.session.Session(session=self.model.selected_session))
        else:
            return klovve.views.Label(text="There is a list of all sessions from the past on the left hand side."
                                           "\n\nChoose one of them in order to see more details about it.")
    view_for_panel = klovve.ui.computed_property(_)
