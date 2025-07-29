# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import builtins
import enum
import threading
import time
import typing as t

import hallyd
import klovve.driver.loop
import klovve.variable

import krrez.api
import krrez.flow
import krrez.flow.watch
import krrez.seeding.profile_loader
import krrez.ui.apps.seeding.models.finishing
import krrez.ui.apps.seeding.models.new_seeding
import krrez.ui.apps.seeding.models.session
import krrez.ui.apps.seeding.views.finishing
import krrez.ui.apps.seeding.views.new_seeding
import krrez.ui.apps.seeding.views.session
import krrez.ui.models.session
import krrez.ui.apps.seeding.models.main


class Main(klovve.ui.ComposedView[krrez.ui.apps.seeding.models.main.Main]):

    @klovve.event.event_handler(krrez.ui.apps.seeding.views.new_seeding.StartSeedEvent)
    def __handle_start_seed(self, event: krrez.ui.apps.seeding.views.new_seeding.StartSeedEvent) -> None:
        event.stop_processing()
        self.model.handle_start_seed()

    def compose(self):
        if self.model.state == krrez.ui.apps.seeding.models.main.State.FORM:
            return krrez.ui.apps.seeding.views.new_seeding.NewSeeding(
                model=krrez.ui.apps.seeding.models.new_seeding.NewSeeding(
                    all_profiles=self.model.bind.all_profiles,
                    all_target_devices=self.model.bind.all_target_devices,
                    #TODO start_seed_func=self.bind.seed,
                    selected_profile_open_parameters=self.model.bind.selected_profile_open_parameters,
                    additional_seed_config=self.model.bind.additional_seed_config,
                    selected_profile=self.model.bind.selected_profile,
                    selected_target_device=self.model.bind.selected_target_device))

        elif self.model.state == krrez.ui.apps.seeding.models.main.State.AWAIT_SEEDING:
            return klovve.views.BusyAnimation()

        elif self.model.state == krrez.ui.apps.seeding.models.main.State.SEEDING:
            return krrez.ui.apps.seeding.views.session.Session(
                model=krrez.ui.apps.seeding.models.session.Session(
                    session=self.model.bind.seed_session,
                    after_seeding_summary_message=self.model.bind.after_seeding_summary_message,
                    do_finishing=self.model.bind.finish_from_here))

        elif self.model.state == krrez.ui.apps.seeding.models.main.State.AWAIT_FINISHING:
            return klovve.views.BusyAnimation(
                text=f"Please start the target machine as described before. Things should then go on here a few minutes"
                     f" later.\n\nIf not, there might be a network issue.\n\nRemember that you can always log in to the"
                     f" target machine and finish the installation this way instead.\n\n"
                     f"     User name: {self.model.seed_user.username}  /  Password: {self.model.seed_user.password}")

        elif self.model.state == krrez.ui.apps.seeding.models.main.State.FINISHING:
            return krrez.ui.apps.seeding.views.finishing.Finishing(
                model=krrez.ui.apps.seeding.views.finishing.Finishing(
                    session=self.model.bind.finish_from_here_session,
                    finish_was_confirmed=self.model.bind.finish_was_confirmed))
