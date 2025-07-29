# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio

import klovve

import krrez.flow.watch
import krrez.ui.views.session
import krrez.ui.models.session
import krrez.ui.apps.runner.models.main


class Main(klovve.ui.ComposedView[krrez.ui.apps.runner.models.main.Main]):

    def compose(self):
        if self.model.installing_session:
            return krrez.ui.views.session.SessionWithFinishConfirmation(
                model=krrez.ui.models.session.SessionWithFinishConfirmation(
                    common=krrez.ui.models.session.Session(
                        session=self.model.installing_session,
                        was_successful=self.model.bind.was_successful),
                    with_finish_confirmation=self.model.bind.confirm_after_installation,
                    finish_was_confirmed=self.model.bind.done))
