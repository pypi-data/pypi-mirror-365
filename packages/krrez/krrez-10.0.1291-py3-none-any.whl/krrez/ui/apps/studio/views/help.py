# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.asset.data


class Help(klovve.ui.ComposedView):

    def compose(self):
        return klovve.views.viewer.Pdf(source=krrez.asset.data.readme_pdf("en"))
