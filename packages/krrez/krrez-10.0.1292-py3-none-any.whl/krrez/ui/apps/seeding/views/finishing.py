# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow
import krrez.ui.views.session
import krrez.ui.models.session
import krrez.ui.apps.seeding.models.finishing


class Finishing(klovve.ui.ComposedView[krrez.ui.apps.seeding.models.finishing.Finishing]):

    def compose(self):
        return krrez.ui.views.session.SessionWithFinishConfirmation(
            model=krrez.ui.models.session.SessionWithFinishConfirmation(
                common=krrez.ui.models.session.Session(session=self.model.session),
                finish_was_confirmed=self.model.bind.finish_was_confirmed))
