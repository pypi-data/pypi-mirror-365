# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio
import threading

import hallyd
import klovve.driver.loop
import klovve.variable

import krrez.flow.dialog
import krrez.flow.logging
import krrez.flow.watch
import krrez.ui.models.session_interaction


class Session(klovve.model.Model):

    session: krrez.flow.Session|None = klovve.model.property()

    entries: list[klovve.views.LogPager.Entry] = klovve.model.list_property()

    bit_graph_image_svg: bytes|None = klovve.model.property(is_settable=False)

    state_text: str = klovve.model.property(initial="", is_settable=False)

    progress: float = klovve.model.property(initial=0, is_settable=False)

    is_finished: bool = klovve.model.property(initial=False, is_settable=False)

    was_successful: bool|None = klovve.model.property(is_settable=False)

    headered_state: klovve.views.HeadBar.Style = klovve.model.property(initial=klovve.views.HeadBar.Style.BUSY,
                                                                       is_settable=False)

    show_tree: bool = klovve.model.property(initial=False)

    verbose: bool = klovve.model.property(initial=False)

    actions: list[klovve.ui.View] = klovve.model.list_property()

    interactions: list["krrez.ui.models.session_interaction.SessionInteraction"] = klovve.model.list_property()

    _session_watch: krrez.flow.watch.Watch|None = klovve.model.property(is_settable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        klovve.effect.activate_effect(self.__refresh_session, owner=self)

    async def __refresh_session(self):
        self._introspect.set_property_value(Session.headered_state, klovve.views.HeadBar.Style.NEUTRAL)

        if not (session := self.session):
            return

        with klovve.variable.no_dependency_tracking():

            self.__interaction_request_fetcher = session.context._interaction_request_fetcher_for_session(
                session, _SessionViewConfigValuesProvider(self, asyncio.get_running_loop()))
            self.__interaction_request_fetcher.__enter__()  # TODO __exit__ ?!

            self.__last_installed_bits_count = -1
            self.__block_nodes = {}
            self.__previous_state = None

            self._introspect.set_property_value(Session._session_watch, krrez.flow.watch.Watch(
                session, log_block_arrived_handler=self.__block_arrived,
                log_block_changed_handler=self.__block_data_changed,
                bit_graph_image_changed_handler=self.__bit_graph_image_changed,
                status_changed_handler=self.__infos_changed))

            # TODO unregister?
            self.__infos_changed()
            #                yy = self.session_watch.__exit__
            #               self.session_watch.__exit__ = lambda *a: (yy(*a), my_session_watch.__exit__(*a))
            #                self.session_watch.__enter__()
            self._session_watch.__enter__()  # TODO

    @klovve.driver.loop.in_driver_loop
    def __block_arrived(self, parent_block_id, block_id, message, began_at, only_single_time, severity):
        if not block_id:
            return
        parent_block_node = self.__block_nodes[parent_block_id] if parent_block_id else self
        new_block = klovve.views.LogPager.Entry()
        new_block.message = message
        new_block.began_at = began_at
        new_block.only_verbose = severity < krrez.flow.logging.Severity.INFO
        new_block.only_single_time = only_single_time
        parent_block_node.entries.append(new_block)
        self.__block_nodes[block_id] = new_block

    @klovve.driver.loop.in_driver_loop
    def __block_data_changed(self, block_id, ended_at):
        self.__block_nodes[block_id].ended_at = ended_at

    @klovve.driver.loop.in_driver_loop
    def __bit_graph_image_changed(self, bit_graph_image_svg):
        self._introspect.set_property_value(Session.bit_graph_image_svg, bit_graph_image_svg)

    @klovve.driver.loop.in_driver_loop
    def __infos_changed(self):
        if len(self._session_watch.installed_bits) != self.__last_installed_bits_count:
            self.__last_installed_bits_count = len(self._session_watch.installed_bits)
            self._introspect.set_property_value(Session.progress, self._session_watch.progress)
        if self._session_watch.ended_at:
            self._introspect.set_property_value(Session.was_successful, self._session_watch.was_successful)
            self._introspect.set_property_value(Session.is_finished, True)
            if self._session_watch.was_successful:
                self._introspect.set_property_value(Session.headered_state, klovve.views.HeadBar.Style.SUCCESSFUL)
            else:
                self._introspect.set_property_value(Session.headered_state, klovve.views.HeadBar.Style.FAILED)
        else:
            self._introspect.set_property_value(Session.headered_state, klovve.views.HeadBar.Style.BUSY)
        state_text = self._session_watch.state_text
        state = (self._session_watch.began_at, self._session_watch.ended_at, self._session_watch.was_successful,
                 state_text)
        if state != self.__previous_state:
            self.__previous_state = state
            self._introspect.set_property_value(Session.state_text, state_text)


class SessionWithFinishConfirmation(klovve.model.Model):

    common: Session|None = klovve.model.property()

    with_finish_confirmation: bool = klovve.model.property(initial=True)

    finish_was_confirmed: bool = klovve.model.property(initial=False)


class _SessionViewConfigValuesProvider(krrez.flow.dialog.Provider,
                                       hallyd.lang.AllAbstractMethodsProvidedByTrick[krrez.flow.dialog.Provider]):

    def __init__(self, session: Session, event_loop: asyncio.BaseEventLoop):
        self.__session_view = session
        self.__requests = {}
        self.__event_loop = event_loop

    def __interact(self, kind: str, *args, **kwargs):
        future = self.__event_loop.create_future()

        def begin_ui_interaction():

            @klovve.driver.loop.in_driver_loop
            def do():
                request = krrez.ui.models.session_interaction.SessionInteraction(method_name=kind, args=args,
                                                                                 kwargs=kwargs)
                self.__session_view.interactions.append(request)
                self.__requests[request] = request

                @klovve.driver.loop.in_driver_loop
                def __set_request_answer(_):
                    request.answer = "TODO cancelled"

                future.add_done_callback(__set_request_answer)

                def __set_future_result():
                    if request.answer is not None and not future.done():
                        future.set_result(request.answer)
                        self.__requests.pop(request)
                        self.__session_view.interactions.remove(request)

                klovve.effect.activate_effect(__set_future_result, owner=request)

            do()

        threading.Thread(target=begin_ui_interaction, daemon=True).start()
        return future

    def __getattribute__(self, item):
        if (not item.startswith("_")) and (item in dir(krrez.flow.dialog.Endpoint)):
            def method(*args, **kwargs):
                return self.__interact(item, *args, **kwargs)
            return method
        return super().__getattribute__(item)
