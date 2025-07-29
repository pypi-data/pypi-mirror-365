# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import contextlib
import typing as t

import hallyd
import klovve

import krrez.api
import krrez.coding
import krrez.ui.apps.dev_lab.models.bit_editor
import krrez.ui.apps.dev_lab.models.profile_editor
import krrez.ui.apps.dev_lab.models.test_editor
import krrez.ui.apps.dev_lab.models.test_plan_editor
import krrez.ui.apps.dev_lab.views.bit_editor
import krrez.ui.apps.dev_lab.views.profile_editor
import krrez.ui.apps.dev_lab.views.test_editor
import krrez.ui.apps.dev_lab.views.test_plan_editor
import krrez.ui.models.list_panel
import krrez.ui.views.list_panel
import krrez.flow.bit_loader
import krrez.seeding.profile_loader
import krrez.ui.apps.dev_lab.models.main


class Main(klovve.ui.ComposedView[krrez.ui.apps.dev_lab.models.main.Main]):

    def _(self):
        if not self.model:
            return None
        if not self.model.selected_custom_bit:
            return klovve.views.Label(text="Create a new Bit or choose an existing one in order to see more details.")
        return krrez.ui.apps.dev_lab.views.bit_editor.BitEditor(
            model=krrez.ui.apps.dev_lab.models.bit_editor.BitEditor(
                bit=self.model.selected_custom_bit))
    view_for_bit_panel = klovve.ui.computed_property(_)

    def _(self):
        if not self.model:
            return None
        if not self.model.selected_custom_profile:
            return klovve.views.Label(text="Create a new Profile or choose an existing one in order to see more details.")
        return krrez.ui.apps.dev_lab.views.profile_editor.ProfileEditor(
            model=krrez.ui.apps.dev_lab.models.profile_editor.ProfileEditor(
                profile=self.model.bind.selected_custom_profile,
                all_normal_bits=self.model.bind.all_normal_bits))
    view_for_profile_panel = klovve.ui.computed_property(_)

    def _(self):
        if not self.model:
            return None
        if not self.model.selected_custom_test:
            return klovve.views.Label(text="Create a new Test or choose an existing one in order to see more details.")
        return krrez.ui.apps.dev_lab.views.test_editor.TestEditor(
            model=krrez.ui.apps.dev_lab.models.test_editor.TestEditor(
                test_class=self.model.bind.selected_custom_test,
                all_profile_test_names=self.model.bind.all_profile_test_names))
    view_for_test_panel = klovve.ui.computed_property(_)

    def _(self):
        if not self.model:
            return None
        if not self.model.selected_custom_test_plan:
            return klovve.views.Label(text="Create a new Test Plan or choose an existing one in order to see more details.")
        return krrez.ui.apps.dev_lab.views.test_plan_editor.TestPlanEditor(
            model=krrez.ui.apps.dev_lab.models.test_plan_editor.TestPlanEditor(
                test_plan=self.model.bind.selected_custom_test_plan,
                all_test_names=self.model.bind.all_test_names,
                all_test_plan_names=self.model.bind.all_test_plan_names,
                all_profile_test_names=self.model.bind.all_profile_test_names))
    view_for_test_plan_panel = klovve.ui.computed_property(_)

    def compose(self):
        return klovve.views.Tabbed(
            tabs=[
                klovve.views.Tabbed.Tab(
                    title="Bits",
                    body=krrez.ui.views.list_panel.ListPanel(
                        model=krrez.ui.models.list_panel.ListPanel(
                            items=self.model.bind.all_custom_bits,
                            selected_item=self.model.bind.selected_custom_bit,
                            body=self.bind.view_for_bit_panel,
                            item_label_func=lambda bit: bit.name,
                            list_actions=[
                                klovve.views.Button(text="Create new Bit", action_name="create_new_bit")]))),
                klovve.views.Tabbed.Tab(
                    title="Profiles",
                    body=krrez.ui.views.list_panel.ListPanel(
                        model=krrez.ui.models.list_panel.ListPanel(
                            items=self.model.bind.all_custom_profiles,
                            selected_item=self.model.bind.selected_custom_profile,
                            body=self.bind.view_for_profile_panel,
                            item_label_func=lambda profile_tuple: profile_tuple[0].name,
                            list_actions=[
                                klovve.views.Button(text="Create new Profile", action_name="create_new_profile")]))),
                klovve.views.Tabbed.Tab(
                    title="Tests",
                    body=krrez.ui.views.list_panel.ListPanel(
                        model=krrez.ui.models.list_panel.ListPanel(
                            items=self.model.bind.all_custom_tests,
                            selected_item=self.model.bind.selected_custom_test,
                            body=self.bind.view_for_test_panel,
                            item_label_func=lambda test_bit: krrez.coding.Tests.bit_name_to_test_name(
                                krrez.flow.bit_loader.bit_name(test_bit)),
                            list_actions=[
                                klovve.views.Button(text="Create new Test", action_name="create_new_test")]))),
                klovve.views.Tabbed.Tab(
                    title="Test Plans",
                    body=krrez.ui.views.list_panel.ListPanel(
                        model=krrez.ui.models.list_panel.ListPanel(
                            items=self.model.bind.all_custom_test_plans,
                            selected_item=self.model.bind.selected_custom_test_plan,
                            body=self.bind.view_for_test_plan_panel,
                            item_label_func=lambda test_plan_bit: krrez.coding.TestPlans.bit_name_to_test_plan_name(
                                krrez.flow.bit_loader.bit_name(test_plan_bit)),
                            list_actions=[
                                klovve.views.Button(text="Create new Test Plan", action_name="create_new_test_plan")])))])

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveBitEvent)
    def __handle_remove_bit(self, event: krrez.ui.apps.dev_lab.models.main.RemoveBitEvent) -> None:
        self.model.handle_remove_bit(event.bit)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveProfileEvent)
    def __handle_remove_profile(self, event: krrez.ui.apps.dev_lab.models.main.RemoveProfileEvent) -> None:
        self.model.handle_remove_profile(event.profile, event.test_bit)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveTestEvent)
    def __handle_remove_test(self, event: krrez.ui.apps.dev_lab.models.main.RemoveTestEvent) -> None:
        self.model.handle_remove_test(event.test)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveTestPlanEvent)
    def __handle_remove_test_plan(self, event: krrez.ui.apps.dev_lab.models.main.RemoveTestPlanEvent) -> None:
        self.model.handle_remove_test_plan(event.test_plan)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.AddBitToProfileEvent)
    def __handle_add_bit_to_profile(self, event: krrez.ui.apps.dev_lab.models.main.AddBitToProfileEvent) -> None:
        self.model.handle_add_bit_to_profile(event.bit_name, event.profile)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveBitFromProfileEvent)
    def __handle_remove_bit_from_profile(self, event: krrez.ui.apps.dev_lab.models.main.RemoveBitFromProfileEvent) -> None:
        self.model.handle_remove_bit_from_profile(event.bit_name, event.profile)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.AddTestToTestPlanEvent)
    def __handle_add_test_to_test_plan(self, event: krrez.ui.apps.dev_lab.models.main.AddTestToTestPlanEvent) -> None:
        self.model.handle_add_test_to_test_plan(event.test_name, event.test_plan)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveTestFromTestPlanEvent)
    def __handle_remove_test_from_test_plan(self, event: krrez.ui.apps.dev_lab.models.main.RemoveTestFromTestPlanEvent) -> None:
        self.model.handle_remove_test_from_test_plan(event.test_name, event.test_plan)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.AddTestPlanToTestPlanEvent)
    def __handle_add_test_plan_to_test_plan(self, event: krrez.ui.apps.dev_lab.models.main.AddTestPlanToTestPlanEvent) -> None:
        self.model.handle_add_test_plan_to_test_plan(event.test_plan_name, event.test_plan)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveTestPlanFromTestPlanEvent)
    def __handle_remove_test_plan_from_test_plan(self, event: krrez.ui.apps.dev_lab.models.main.RemoveTestPlanFromTestPlanEvent) -> None:
        self.model.handle_remove_test_plan_from_test_plan(event.test_plan_name, event.test_plan)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.AddTestProfileToTestPlanEvent)
    def __handle_add_profile_test_to_test_plan(self, event: krrez.ui.apps.dev_lab.models.main.AddTestProfileToTestPlanEvent) -> None:
        self.model.handle_add_profile_test_to_test_plan(event.test_profile_name, event.test_plan)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveTestProfileFromTestPlanEvent)
    def __handle_remove_profile_test_from_test_plan(self, event: krrez.ui.apps.dev_lab.models.main.RemoveTestProfileFromTestPlanEvent) -> None:
        self.model.handle_remove_profile_test_from_test_plan(event.test_profile_name, event.test_plan)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.AddProfileToTestEvent)
    def __handle_add_profile_to_test(self, event: krrez.ui.apps.dev_lab.models.main.AddProfileToTestEvent) -> None:
        self.model.handle_add_profile_to_test(event.profile_name, event.test)

    @klovve.event.event_handler(krrez.ui.apps.dev_lab.models.main.RemoveProfileFromTestEvent)
    def __handle_remove_profile_from_test(self, event: krrez.ui.apps.dev_lab.models.main.RemoveProfileFromTestEvent) -> None:
        self.model.handle_remove_profile_from_test(event.profile_name, event.test)

    @klovve.event.action("create_new_bit")
    async def __handle_create_new_bit(self, event):
        krrez_module_directory = await self.__target_directory(event, "Where do you want to create the new Bit?")
        if not krrez_module_directory:
            return
        new_name = await self.application.dialog(klovve.views.interact.TextInput(
            message="Please enter a name for the new Bit."),
            view_anchor=event.triggering_view)
        if not new_name:
            return
        async with self.__error_message_for_exception(event.triggering_view):
            self.model.handle_create_new_bit(krrez_module_directory, new_name)

    @klovve.event.action("create_new_profile")
    async def __handle_create_new_profile(self, event):
        krrez_module_directory = await self.__target_directory(event, "Where do you want to create the new Profile?")
        if not krrez_module_directory:
            return
        new_name = await self.application.dialog(klovve.views.interact.TextInput(
            message="Please enter a name for the new Profile."),
            view_anchor=event.triggering_view)
        if not new_name:
            return
        async with self.__error_message_for_exception(event.triggering_view):
            self.model.handle_create_new_profile(krrez_module_directory, new_name)

    @klovve.event.action("create_new_test_plan")
    async def __handle_create_new_test_plan(self, event):
        krrez_module_directory = await self.__target_directory(event, "Where do you want to create the new Test Plan?")
        if not krrez_module_directory:
            return
        new_name = await self.application.dialog(klovve.views.interact.TextInput(
            message="Please enter a name for the new Test Plan."),
            view_anchor=event.triggering_view)
        if not new_name:
            return
        async with self.__error_message_for_exception(event.triggering_view):
            self.model.handle_create_new_test_plan(krrez_module_directory, new_name)

    @klovve.event.action("create_new_test")
    async def __handle_create_new_test(self, event):
        krrez_module_directory = await self.__target_directory(event, "Where do you want to create the new Test?")
        if not krrez_module_directory:
            return
        new_name = await self.application.dialog(klovve.views.interact.TextInput(
            message="Please enter a name for the new Test."),
            view_anchor=event.triggering_view)
        if not new_name:
            return
        async with self.__error_message_for_exception(event.triggering_view):
            self.model.handle_create_new_test(krrez_module_directory, new_name)

    @contextlib.asynccontextmanager
    async def __error_message_for_exception(self, triggering_view: klovve.ui.View):
        try:
            yield
        except Exception as ex:
            await triggering_view.application.dialog(klovve.views.interact.Message(
                message=str(ex),
                choices=[("OK", None)]
            ), view_anchor=triggering_view)

    async def __target_directory(self, event, message) -> t.Optional[krrez.api.Path]:
        krrez_module_directories = krrez.flow.bit_loader.krrez_module_directories(with_builtin=False)
        if len(krrez_module_directories) == 0:
            TODO
        elif len(krrez_module_directories) == 1:
            return krrez_module_directories[0]
        else:
            if (krrez_module_directory := await self.application.dialog(klovve.views.interact.Message(
                    message=message,
                    choices=krrez_module_directories),
                    view_anchor=event.triggering_view)) is not None:
                return krrez_module_directory
