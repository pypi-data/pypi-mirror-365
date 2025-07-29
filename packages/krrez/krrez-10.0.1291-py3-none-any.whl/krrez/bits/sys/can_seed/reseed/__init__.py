# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Installation of the Krrez reseed mechanism. It allows to reinstall Krrez without touching the machine, in particular
without attaching bootable external storage.
"""
import typing as t

import hallyd

import krrez.api
import krrez.bits.sys.shell.core
import krrez.flow
import krrez.seeding.reseed


class Bit(krrez.api.Bit):

    _shell: krrez.bits.sys.shell.core.Bit
    __later: krrez.api.Later["krrez.bits.sys.can_seed.Bit"]

    _update_handlers_path = krrez.flow.KRREZ_USR_DIR("reseed_update_handlers")

    _keep_configvalues = krrez.api.ConfigValue(default=[], type=list[str])

    def __apply__(self):
        self._packages.install("python3-venv")

        self._shell.create_command(Bit.reseed, bit_short_name="seed")

        self._update_handlers_path.make_dir()
        self.install_update_handlers()

    def install_update_handlers(self, *, path: t.Optional[hallyd.fs.TInputPath] = None,
                                base_name: t.Optional[str] = "") -> None:
        """
        Install reseed update handlers.

        :param path: The source directory path (default: :file:`.../-data/-reseed_update_handlers`).
        :param base_name: The base name. Only needed when called outside a Krrez session. Use with care.
        """
        self._helpers.install_files(path, base_name, default_dir_name="-reseed_update_handlers",
                                    destination_dir=self._update_handlers_path)

    def keep_config_value(self, config: "krrez.api.ConfigValue") -> None:
        if not config.full_name:
            raise ValueError("`keep_config_value` must be used with config values from Bit _instances_, not types")
        with self._keep_configvalues as x:
            x.value.append(config.full_name)

    def reseed(self, *, i_understood_that_this_purges_my_system: bool = False,
               backup_connection_name: t.Union[str, bool, None] = None) -> None:  # TODO dedup (seeding/reseed/__init__.py run)
        """
        Reseed the current machine with an updated version of Krrez and its auxiliary packages.

        :param i_understood_that_this_purges_my_system: Set to :code:`True` if you understand that this will remove
                                                        all data on your system as well as the system itself.
        :param backup_connection_name: The backup connection name for the final backup.
        """
        if not i_understood_that_this_purges_my_system:
            raise ValueError("this method will reinstall this system completely, purging everything including all your"
                             " data; You have to confirm that by calling this method again, setting the parameter"
                             " i_understood_that_this_purges_my_system=True")

        krrez.seeding.reseed.run(backup_connection_name=backup_connection_name)
