# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import krrez.api


class Bit(krrez.api.Bit):

    def __apply__(self):
        machine_avatar_mod = self._data_dir("krrez_machine_avatar.py")
        machine_avatar_mod.copy_to(self._fs.python_site_modules_dir(machine_avatar_mod.name), readable_by_all=True)

    def avatar(self, machine_hostname: t.Optional[str] = None, **kwargs) -> str:
        import krrez_machine_avatar
        return krrez_machine_avatar.avatar(machine_hostname, **kwargs)
