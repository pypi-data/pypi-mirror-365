# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow


class Finishing(klovve.model.Model):

    session: krrez.flow.Session|None = klovve.model.property()

    finish_was_confirmed: bool = klovve.model.property(initial=False)
