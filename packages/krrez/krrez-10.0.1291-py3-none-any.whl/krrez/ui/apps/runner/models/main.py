# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve

import krrez.flow.watch
import krrez.flow.runner
import krrez.ui


class Main(klovve.model.Model):

    krrez_application: krrez.ui.Application = klovve.model.property()

    bit_names: t.Iterable[str]|None = klovve.model.property()

    engine: krrez.flow.runner.Engine|None = klovve.model.property()

    confirm_after_installation: bool = klovve.model.property(initial=False)

    done: bool = klovve.model.property(initial=False)

    was_successful: bool|None = klovve.model.property()

    async def _(self):
        if self.bit_names is not None and self.krrez_application and self.engine:
            return self.engine.start(context=self.krrez_application.runtime_data.context,
                                     bit_names=self.bit_names).session
    installing_session: krrez.flow.watch.Watch|None = klovve.model.computed_property(_)
