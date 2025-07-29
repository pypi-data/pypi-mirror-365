# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui.apps.studio.models.welcome


class Welcome(klovve.ui.ComposedView[krrez.ui.apps.studio.models.welcome.Welcome]):

    def compose(self):
        return klovve.views.TextBlock(text=self.model.bind.text_html)
