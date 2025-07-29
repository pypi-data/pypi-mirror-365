# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow
import krrez.ui.views.session
import krrez.ui.models.session
import krrez.ui.apps.seeding.models.session


class Session(klovve.ui.ComposedView[krrez.ui.apps.seeding.models.session.Session]):

    def _(self):
        if not self.model:
            return None
        if self.model.after_seeding_summary_message:
            return klovve.views.interact.Message(message=self.model.bind.after_seeding_summary_message,
                                                 choices=[("Finish the seeding from here", 0), ("I'm done here", 1)],
                                                 answer=self.model.bind.after_seeding_summary_message_answer)
    view_for_summary = klovve.ui.computed_property(_)

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                krrez.ui.views.session.Session(model=krrez.ui.models.session.Session(session=self.model.session)),
                klovve.views.Placeholder(
                    body=self.bind.view_for_summary,
                    vertical_layout=klovve.ui.Layout(klovve.ui.Align.FILL))])
