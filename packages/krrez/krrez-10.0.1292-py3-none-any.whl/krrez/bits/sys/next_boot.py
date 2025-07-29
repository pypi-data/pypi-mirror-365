# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import hallyd

import krrez.api.internal


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):
    """
    Management of operating system next-boot tasks.
    """

    def create_task(self, name: t.Optional[str],
                    runnable: "hallyd.services.TRunnable") -> t.ContextManager["hallyd.services.NextBootTaskSetup"]:
        return hallyd.services.create_next_boot_task(name, runnable)
