# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve

import krrez.flow.runner
import krrez.ui.views.window


class Application(krrez.ui.Application):

    bit_names: t.Iterable[str]|None = klovve.model.property()

    engine: krrez.flow.runner.Engine|None = klovve.model.property()

    confirm_after_installation: bool = klovve.model.property(initial=False)

    installing_session: krrez.flow.Session|None = klovve.model.property()

    done: bool = klovve.model.property(initial=False)

    was_successful: bool|None = klovve.model.property()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from krrez.ui.apps.runner.models.main import Main as MainModel
        from krrez.ui.apps.runner.views.main import Main as MainView

        self.windows.append(krrez.ui.views.window.Window(
            title="Krrez",
            body=MainView(
                model=MainModel(
                    krrez_application=self,
                    bit_names=self.bind.bit_names,
                    engine=self.bind.engine,
                    confirm_after_installation=self.bind.confirm_after_installation,
                    installing_session=self.bind.installing_session,
                    done=self.bind.done,
                    was_successful=self.bind.was_successful))))

        klovve.effect.activate_effect(self.__refresh_window_closed, owner=self)

    def __refresh_window_closed(self):
        if self.done:
            self.windows[0].close()
