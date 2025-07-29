# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow
import krrez.ui


class Main(klovve.model.Model):

    krrez_application: krrez.ui.Application = klovve.model.property()

    all_sessions: list[krrez.flow.Session] = klovve.model.list_property()

    selected_session: krrez.flow.Session|None = klovve.model.property()

    @klovve.timer.run_timed(interval=60)
    def __refresh_all_sessions(self):
        self.all_sessions = reversed(self.krrez_application.runtime_data.context.get_sessions())
