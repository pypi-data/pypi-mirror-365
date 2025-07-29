# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import krrez.ui.models.session_interaction


class SessionInteraction(klovve.ui.ComposedView[krrez.ui.models.session_interaction.SessionInteraction]):

    def compose(self):
        answer = dict(answer=self.model.bind.answer)

        if self.model.method_name == "choose":
            if isinstance((choices := self.model.kwargs["choices"]), dict):
                choices_ = choices.items()
            else:
                choices_ = [(str(_), _) for _ in choices]
            return klovve.views.interact.Message(message=self.model.args[0], choices=choices_, **answer)

        if self.model.method_name == "input":
            return klovve.views.interact.TextInput(message=self.model.args[0], **answer)
