# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui.apps.dev_lab.models.main
import krrez.ui.apps.dev_lab.views.main
import krrez.ui.apps.log_browser.models.main
import krrez.ui.apps.log_browser.views.main
import krrez.ui.apps.seeding.models.main
import krrez.ui.apps.seeding.views.main
import krrez.ui.apps.studio.views.help
import krrez.ui.apps.studio.models.welcome
import krrez.ui.apps.studio.models.main
import krrez.ui.apps.studio.views.welcome
import krrez.ui.apps.testing.models.main
import krrez.ui.apps.testing.views.main
import krrez.flow


class Main(klovve.ui.ComposedView[krrez.ui.apps.studio.models.main.Main]):

    class Tab:

        is_only_for_krrez_machines = False

        def view(self, visible_tab_names: list[str]):
            pass

    def _(self):
        if not self.model:
            return ()

        main_view = self
        class Welcome(Main.Tab):

            def view(self, visible_tab_names):
                return klovve.views.Tabbed.Tab(
                    title="Welcome",
                    body=krrez.ui.apps.studio.views.welcome.Welcome(
                        model=krrez.ui.apps.studio.models.welcome.Welcome(
                            visible_tab_names=visible_tab_names)))

        class Logs(Main.Tab):

            is_only_for_krrez_machines = True

            def view(self, visible_tab_names):
                return klovve.views.Tabbed.Tab(title="Logs", body=krrez.ui.apps.log_browser.views.main.Main(
                    model=krrez.ui.apps.log_browser.models.main.Main(
                        krrez_application=main_view.model.bind.krrez_application)))

        class Seeding(Main.Tab):

            def view(self, visible_tab_names):
                return klovve.views.Tabbed.Tab(title="Seeding", body=krrez.ui.apps.seeding.views.main.Main(
                    model=krrez.ui.apps.seeding.models.main.Main(
                        krrez_application=main_view.model.bind.krrez_application)))

        class Development(Main.Tab):

            def view(self, visible_tab_names):
                return klovve.views.Tabbed.Tab(title="Development", body=krrez.ui.apps.dev_lab.views.main.Main(
                    model=krrez.ui.apps.dev_lab.models.main.Main(
                        krrez_application=main_view.model.bind.krrez_application)))

        class Testing(Main.Tab):

            def view(self, visible_tab_names):
                return klovve.views.Tabbed.Tab(title="Testing", body=krrez.ui.apps.testing.views.main.Main(
                    model=krrez.ui.apps.testing.models.main.Main(
                        krrez_application=main_view.model.bind.krrez_application)))

        class Help(Main.Tab):

            def view(self, visible_tab_names):
                return klovve.views.Tabbed.Tab(
                    title="Help",
                    body=krrez.ui.apps.studio.views.help.Help(
                        visible_tab_names=visible_tab_names))

        is_krrez_machine = krrez.flow.is_krrez_machine()
        visible_tabs = [tab_type() for tab_type in [Welcome, Logs, Seeding, Development, Testing, Help]
                        if is_krrez_machine or not tab_type.is_only_for_krrez_machines]

        visible_tab_names = [type(t).__name__ for t in visible_tabs]

        return [tab.view(visible_tab_names) for tab in visible_tabs]
    tabs: list[Tab] = klovve.model.computed_property(_)

    def compose(self):
        return klovve.views.Tabbed(tabs=self.bind.tabs)
