# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import hallyd

import krrez.api.internal


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):
    """
    Management of operating system services.
    """

    def create_service(self, name: t.Optional[str],
                       runnable: "hallyd.services.TRunnable") -> t.ContextManager["hallyd.services.ServiceSetup"]:
        return hallyd.services.create_service(name, runnable)

    def remove_service(self, service: hallyd.services.TServiceKey) -> None:
        return hallyd.services.remove_service(service)

    def start_service(self, service: hallyd.services.TServiceKey) -> None:
        return hallyd.services.service(service).start()

    def stop_service(self, service: hallyd.services.TServiceKey) -> None:
        return hallyd.services.service(service).stop()

    def restart_service(self, service: hallyd.services.TServiceKey) -> None:
        return hallyd.services.service(service).restart()

    def reload_service(self, service: hallyd.services.TServiceKey) -> None:
        return hallyd.services.service(service).reload()

    def enable_service(self, service: hallyd.services.TServiceKey) -> None:
        return hallyd.services.service(service).enable()

    def disable_service(self, service: hallyd.services.TServiceKey) -> None:
        return hallyd.services.service(service).disable()

    def is_service_active(self, service: hallyd.services.TServiceKey) -> bool:
        return hallyd.services.service(service).is_active()

    def override(self, service: hallyd.services.TServiceKey, *, wants: list[str] = (), requires: list[str] = (),
                 after: list[str] = (), before: list[str] = (),
                 wanted_by: list[str] = (), required_by: list[str] = (),
                 reset_wants: bool = False, reset_requires: bool = False,
                 reset_after: bool = False, reset_before: bool = False,
                 reset_wanted_by: bool = False, reset_required_by: bool = False) -> None:
        return hallyd.services.service(service).override(wants=wants, requires=requires, after=after, before=before,
                                                         wanted_by=wanted_by, required_by=required_by,
                                                         reset_wants=reset_wants, reset_requires=reset_requires,
                                                         reset_after=reset_after, reset_before=reset_before,
                                                         reset_wanted_by=reset_wanted_by,
                                                         reset_required_by=reset_required_by)

    def create_interval_task(self, name: t.Optional[str], runnable: "hallyd.services.TRunnable"
                             ) -> t.ContextManager["hallyd.services.IntervalTaskSetup"]:
        return hallyd.services.create_interval_task(name, runnable)

    def remove_interval_task(self, name: str) -> None:
        return hallyd.services.remove_interval_task(name)

    def create_calendar_task(self, name: t.Optional[str], runnable: "hallyd.services.TRunnable"
                             ) -> t.ContextManager["hallyd.services.CalendarTaskSetup"]:
        return hallyd.services.create_calendar_task(name, runnable)

    def remove_calendar_task(self, name: str) -> None:
        return hallyd.services.remove_calendar_task(name)
