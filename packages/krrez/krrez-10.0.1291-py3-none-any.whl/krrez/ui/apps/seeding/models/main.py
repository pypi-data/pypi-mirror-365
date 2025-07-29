# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio
import builtins
import enum
import threading
import time

import hallyd
import klovve.driver.loop
import klovve.variable

import krrez.api.internal
import krrez.flow
import krrez.seeding.profile_loader


class State(enum.Enum):
    FORM = enum.auto()
    AWAIT_SEEDING = enum.auto()
    SEEDING = enum.auto()
    AWAIT_FINISHING = enum.auto()
    FINISHING = enum.auto()


class Profile(klovve.model.Model):

    name: str = klovve.model.property()

    type: builtins.type[krrez.api.Profile] = klovve.model.property()  # TODO

    def __eq__(self, other):  # TODO eq/hash for mutables?!
        return isinstance(other, type(self)) and other.type == self.type

    def __hash__(self):
        return hash(self.type)


class Target(klovve.model.Model):

    path: hallyd.fs.Path = klovve.model.property()

    description: str = klovve.model.property()

    def _(self):
        return f"{self.description} ({self.path})"
    label: str = klovve.model.computed_property(_)

    def __eq__(self, other):  # TODO eq/hash for mutables?!
        return isinstance(other, type(self)) and other.path == self.path

    def __hash__(self):
        return hash(self.path)


class Main(klovve.model.Model):

    krrez_application: krrez.ui.Application = klovve.model.property()

    async def _(self):
        for _ in range(10):
            await asyncio.sleep(0)
        if self.start_with:
            with klovve.variable.no_dependency_tracking():
                self.__refresh_available_profiles()
                self.selected_profile = [_ for _ in self.all_profiles if _.name == self.start_with[0]][0]
                self.__refresh_available_targets()
                self.selected_target_device = [_ for _ in self.all_target_devices if str(_.path) == self.start_with[1]][0]
                additional_config = self.start_with[2]
                self.__refresh_profile_open_parameters()
                for profile_parameter in self.selected_profile_open_parameters:
                    if profile_parameter.name in additional_config:
                        self.additional_seed_config[profile_parameter] = additional_config[profile_parameter.name]
                self.handle_start_seed()
    __ = klovve.model.computed_property(_)

    state: State = klovve.model.property(initial=State.FORM, is_settable=False)

    all_profiles: list[Profile] = klovve.model.list_property()

    selected_profile: Profile|None = klovve.model.property()

    seed_user: object = klovve.model.property()

    after_seeding_summary_message: str|None = klovve.model.property()

    finish_was_confirmed: bool = klovve.model.property(initial=False)

    selected_profile_open_parameters: list["krrez.api.Profile.Parameter"] = klovve.model.list_property()

    additional_seed_config: dict["krrez.api.Profile.Parameter", str] = klovve.model.property(initial=lambda: {})

    all_target_devices: list[Target] = klovve.model.list_property()

    selected_target_device: Target|None = klovve.model.property()

    seed_session: krrez.flow.Session|None = klovve.model.property()

    finish_from_here: bool|None = klovve.model.property()

    finish_from_here_session: krrez.flow.Session|None = klovve.model.property()

    start_with: tuple[str, str, dict[str, str]]|None = klovve.model.property()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__seed_thread = None
        klovve.effect.activate_effect(self.__handle_selection_changed, owner=self)

    class _SeedAct(krrez.seeding.SeedAct):

        def __init__(self, main_app: "Model", *, profile: "krrez.api.Profile", target_device: "krrez.api.Path"):
            super().__init__(profile=profile, target_device=target_device)
            self.__main_app = main_app

        def _begin(self):
            self.__main_app.after_seeding_summary_message = None
            self.__main_app.seed_session = self.__main_app.finish_from_here_session = None
            self.__main_app.finish_from_here = None
            self.__main_app.selected_target_device = self.__main_app.selected_profile = None
            self.__main_app.additional_seed_config = {}
            self.__main_app._introspect.set_property_value(Main.state, State.AWAIT_SEEDING)

        def _start_creating_installation_medium(self, watch):
            self.__main_app.seed_session = watch.session
            self.__main_app._introspect.set_property_value(Main.state, State.SEEDING)

        def _installation_medium_created(self, seed_user, seed_strategy):
            self.__main_app.seed_user = seed_user

            message = "Your installation medium is now ready to be used!\n"
            if seed_user:
                message += (f"Please write down the following credentials somewhere. They are only valid during"
                            f" installation.\n"
                            f"     User name: {seed_user.username}  /  Password: {seed_user.password}\n\n")
            message += seed_strategy.next_step_message + "\n\n"
            if seed_user:
                message += (
                    "There are two ways to finish the installation from there: You can either log in to that machine,"
                    " via ssh or locally, with the account from above, and follow the on-screen instructions."
                    " You are done here in that case."
                    " Another way is to finish the installation from here. That needs a network connection to the"
                    " target machine. In case of problems, or for any other reasons, you can just switch to the former"
                    " way whenever you want.")

            self.__main_app.after_seeding_summary_message = message
            while self.__main_app.finish_from_here is None:
                time.sleep(1)
            return self.__main_app.finish_from_here

        def _start_finishing(self):
            self.__main_app._introspect.set_property_value(Main.state, State.AWAIT_FINISHING)

        def _watch_finishing(self, watch):
            self.__main_app.finish_from_here_session = watch.session
            self.__main_app._introspect.set_property_value(Main.state, State.FINISHING)

        def _done(self, *, finish_from_here, unknown):
            if finish_from_here:
                while not self.__main_app.finish_was_confirmed:
                    time.sleep(1)
            self.__main_app._introspect.set_property_value(Main.state, State.FORM)
            self.__main_app.finish_was_confirmed = False

    def seed(self, context):
        profile = self.selected_profile.type.get({k.name: v for k, v in self.additional_seed_config.items()})
        if self.__seed_thread:
            raise RuntimeError("seeding is already in progress")
        self.__seed_thread = threading.Thread(target=self.__seed, args=(profile, self.selected_target_device.path), daemon=True)
        self.__seed_thread.start()

    def handle_start_seed(self) -> None:
        self.seed(self.krrez_application.runtime_data.context)

    def __seed(self, profile, target_device):
        Main._SeedAct(klovve.driver.loop.object_proxy(self), profile=profile, target_device=target_device).seed()
        self.__seed_thread = None

    def __handle_selection_changed(self):
        _ = self.selected_profile, self.selected_target_device

        with klovve.variable.no_dependency_tracking():
            self.__refresh_available_targets()
            self.__refresh_profile_open_parameters()

    @klovve.timer.run_timed(interval=2*60)
    def __refresh_available_profiles(self):
        self.all_profiles = (Profile(name=_.name, type=_) for _ in krrez.seeding.profile_loader.browsable_profiles())

    @klovve.timer.run_timed(interval=60)
    def __refresh_available_targets(self):
        self.all_target_devices = (Target(path=_[0], description=_[1])
                                   for _ in (self.selected_profile.type.available_target_devices if self.selected_profile else []))

    def __refresh_profile_open_parameters(self):
        self.selected_profile_open_parameters = self.selected_profile.type.open_parameters if self.selected_profile else []
