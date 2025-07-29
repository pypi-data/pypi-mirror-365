# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui.views.window


class Application(krrez.ui.Application):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from krrez.ui.apps.studio.models.main import Main as MainModel
        from krrez.ui.apps.studio.views.main import Main as MainView

        self.windows.append(krrez.ui.views.window.Window(
            title="Krrez Studio",
            body=MainView(model=MainModel(krrez_application=self))))
