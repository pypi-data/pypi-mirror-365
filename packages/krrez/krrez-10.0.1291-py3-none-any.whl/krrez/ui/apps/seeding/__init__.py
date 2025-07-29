# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui.views.window


class Application(krrez.ui.Application):

    start_with: tuple[str, str, dict[str, str]]|None = klovve.model.property()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from krrez.ui.apps.seeding.models.main import Main as MainModel
        from krrez.ui.apps.seeding.views.main import Main as MainView

        self.windows.append(krrez.ui.views.window.Window(
            title="Krrez Seeding",
            body=MainView(model=MainModel(
                krrez_application=self,
                start_with=self.bind.start_with))))
