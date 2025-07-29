# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow
import krrez.ui.views.window


class Application(krrez.ui.Application):

    start_with_session: krrez.flow.Session|None = klovve.ui.property()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from krrez.ui.apps.testing.models.main import Main as MainModel
        from krrez.ui.apps.testing.views.main import Main as MainView

        self.windows.append(krrez.ui.views.window.Window(
            title="Krrez Testing",
            body=MainView(model=MainModel(
                krrez_application=self,
                start_with_session=self.bind.start_with_session))))
