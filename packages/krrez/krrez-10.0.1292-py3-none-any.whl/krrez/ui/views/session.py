# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio

import klovve.driver.loop
import klovve.variable

import krrez.flow.dialog
import krrez.flow.logging
import krrez.flow.watch
import krrez.ui.models.session
import krrez.ui.views.session_interaction


class Session(klovve.ui.ComposedView[krrez.ui.models.session.Session]):

    def _(self):
        if not self.model:
            return
        if self.model.show_tree:
            return klovve.views.viewer.Image(
                source=self.model.bind.bit_graph_image_svg,
                horizontal_layout=klovve.ui.Layout(min_size_em=7))
    view_for_tree: klovve.ui.View|None = klovve.ui.computed_property(_)

    def _(self):
        if not self.model:
            return ()
        return [krrez.ui.views.session_interaction.SessionInteraction(model=x) for x in self.model.interactions]
    interaction_views: list[klovve.ui.View] = klovve.ui.computed_list_property(_)

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                klovve.views.HeadBar(
                    title=self.model.bind.state_text,
                    primary_header_views=self.model.bind.actions,
                    secondary_header_views=[
                        klovve.views.CheckButton(text="Show tree", is_checked=self.model.bind.show_tree),
                        klovve.views.CheckButton(text="Verbose", is_checked=self.model.bind.verbose)],
                    style=self.model.bind.headered_state,
                    progress=self.model.bind.progress),
                klovve.views.responsive.Dual(
                    item_1=klovve.views.VerticalBox(
                        items=[
                            klovve.views.LogPager(
                                entries=self.model.bind.entries,
                                show_verbose=self.model.bind.verbose),
                            klovve.views.VerticalBox(
                                items=self.bind.interaction_views,
                                vertical_layout=klovve.ui.Layout(klovve.ui.Align.END))]),
                    item_2=self.bind.view_for_tree)])


class SessionWithFinishConfirmation(klovve.ui.ComposedView[krrez.ui.models.session.SessionWithFinishConfirmation]):

    def _(self):
        if self.model and self.model.common and self.model.common.is_finished:
            if self.model.with_finish_confirmation and not self.model.finish_was_confirmed:
                return klovve.views.interact.Message(message="The installation has been finished.",
                                                     answer=self.model.bind.finish_was_confirmed)
            elif not self.model.with_finish_confirmation:
                self.model.finish_was_confirmed = True
    confirmation_bar: klovve.ui.View|None = klovve.ui.computed_property(_)

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                Session(model=self.model.bind.common),
                klovve.views.Placeholder(
                    body=self.bind.confirmation_bar,
                    vertical_layout=klovve.ui.Layout(klovve.ui.Align.END))])
