# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.flow


class Session(klovve.model.Model):

    session: krrez.flow.Session|None = klovve.model.property()

    do_finishing: bool = klovve.model.property(initial=False)

    after_seeding_summary_message: str|None = klovve.model.property()

    after_seeding_summary_message_answer: int|None = klovve.model.property()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        klovve.effect.activate_effect(self.__refresh_do_finishing, owner=self)

    def __refresh_do_finishing(self):
        if self.after_seeding_summary_message_answer is not None:
            self.do_finishing = self.after_seeding_summary_message_answer == 0
