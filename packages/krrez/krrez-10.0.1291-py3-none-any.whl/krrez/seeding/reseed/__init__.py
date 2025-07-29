# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import glob
import os
import subprocess
import sys
import typing as t
import venv

import hallyd

import krrez.asset.project_info
import krrez.bits.sys.can_seed.reseed
import krrez.flow.bit_loader

# This code creates a new virtual environment with updated package versions and finally hands over to that NEW code in
# order to do the actual reseeding.

# Changes here might break the possibility to reseed from an older version. Whatever you change, make sure that it
# finally calls the module `krrez.seeding.reseed` as a new process in the NEW environment (and hand it over additionally
# required data in a compatible way).

# It is fine to adapt it to new logic, newer Krrez APIs or similar, though, as long as it does not break the behavior
# just mentioned. This even includes the external API of this module, how it is implemented, what modules it imports,
# as well as the implementation of `krrez.seeding.reseed` being called as new process!


def run(*, backup_connection_name: t.Union[str, bool, None] = None,   # TODO also test backup_connection_name!=False
        _for_zz_test: t.Optional[dict] = None,
        _skip_updating: bool = False) -> None:
    """
    Reseed the current machine with an updated version of Krrez and its auxiliary packages.

    :param backup_connection_name: The backup connection name for the final backup.
    :param _for_zz_test: Do not use.
    :param _skip_updating: Do not use.
    """

    # This code is executed in the original environment of the OLD Krrez version. It creates a new virtual environment
    # with updated package versions and finally hands over to that NEW code in order to continue reseeding.

    kept_config = {key: krrez.flow.Context().config.get(key)
                   for key in krrez.asset.bit(krrez.bits.sys.can_seed.reseed.Bit)._keep_configvalues.value}

    profile_type, profile_data = krrez.flow.Context().config.get("profile_created_as")

    # Changes here might break the possibility to reseed from an older version. Whatever you change, be aware that
    # even your new code will receive this data from the OLD version!
    # So, whenever you add a new value here (or remove/restructure existing ones), take care that the new code can
    # handle it being missing!
    reseed_data = {"profile_type": profile_type, "profile_data": profile_data, "kept_config": kept_config,
                   "for_zz_test": _for_zz_test}

    if _skip_updating:
        python_bin = sys.executable

    else:
        krrez_venv_dir = hallyd.fs.Path("/tmp/krrez_reseed_venv").remove(not_exist_ok=True)

        venv_builder = venv.EnvBuilder(with_pip=True)
        venv_builder.create(krrez_venv_dir)
        venv_paths = venv_builder.ensure_directories(krrez_venv_dir)

        lib_path = hallyd.fs.Path(glob.glob(f"{krrez_venv_dir}/lib/*/site-packages")[0])

        krrez_pth_content = ""
        for i, krrez_module_directory in enumerate(krrez.flow.bit_loader.krrez_module_directories(with_builtin=True)):
            new_krrez_module_directory = krrez_venv_dir(str(i))
            new_krrez_module_directory.make_dir(readable_by_all=True)

            krrez_module_directory("krrez").copy_to(new_krrez_module_directory("krrez"), readable_by_all=True)

            # Update handlers will be called as normal executable, so they are running in the OLD environment.
            # They get the new environment as argument, though.
            for reseed_update_handler in sorted(krrez.flow.KRREZ_USR_DIR("reseed_update_handlers").iterdir(),
                                                key=lambda p: p.stem.split(".")[-1]):
                subprocess.check_call([sys.executable, reseed_update_handler, new_krrez_module_directory,
                                       venv_paths.bin_path])

            krrez_pth_content += f"{new_krrez_module_directory}\n"

            requirements_file = new_krrez_module_directory("krrez/runtime-requirements.txt")
            if requirements_file.exists():
                subprocess.check_call([krrez_venv_dir("bin/pip3"), "install", "-r", requirements_file])

        lib_path("krrez.pth").write_text(krrez_pth_content)
        python_bin = krrez_venv_dir("bin/python3")

    if backup_connection_name is not False:
        try:
            import krrez_backup.engine as backup
        except ImportError:
            backup = None
        if backup:
            # TODO improve, test (e.g.: will it really raise an exception if it failed)
            backup.backup(backup_connection_name, verify=True, leave_shut_down_afterwards=True, detachable=False,
                          defer_time=0)

    subprocess.check_call([python_bin, "-m", __name__],
                          env={**os.environb, "KRREZ_RESEED_DATA": hallyd.bindle.dumps(reseed_data),
                               "KRREZ_RESEED_FROM_VERSION": krrez.asset.project_info.version.split(".")[0]})
