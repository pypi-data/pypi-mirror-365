# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui


class Main(klovve.model.Model):

    krrez_application: krrez.ui.Application = klovve.model.property()
