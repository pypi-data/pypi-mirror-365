# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
System level helpers.
"""
import hallyd

import krrez.flow.bit_loader


def turn_into_krrez_system(system_root_path: hallyd.fs.Path, *,
                           install_krrez_packages: bool = True) -> None:
    """
    Turn a target system into a Krrez system.

    This includes copying all Krrez modules to a particular location in the target system, and some additional
    wiring in order to make the 'krrez' command available and enabled (i.e. the target system is marked as Krrez
    machine).

    :param system_root_path: The root directory of the target system to turn into a Krrez system.
    :param install_krrez_packages: If to include copying Krrez packages. If not, you can manually do so by picking up
                                   `/__`.
    """
    system_root_path = hallyd.fs.Path(system_root_path)

    destination_base_path = system_root_path("usr/local/share")

    destination_base_path.make_dir(until="/", exist_ok=True, readable_by_all=True)
    krrez.flow.KRREZ_SRC_ROOT_DIR.copy_to(destination_base_path("krrez"), readable_by_all=True)
    destination_base_path("krrez/krrez_cli.py").change_access(executable=True)

    krrez.flow.mark_as_krrez_machine(system_root_path)

    destination_cli_base_path = system_root_path("usr/local/sbin")
    destination_cli_base_path.make_dir(until=system_root_path, exist_ok=True, readable_by_all=True)
    destination_cli_base_path("krrez").symlink_to("/usr/local/share/krrez/krrez_cli.py")

    krrez_pth_content = ""
    native_target_base_path = hallyd.fs.Path("/usr/local/krrez/additional_modules_hive")

    for i, additional_modules_dir in enumerate(krrez.flow.bit_loader.krrez_module_directories(with_builtin=False)):
        native_target_path = native_target_base_path(str(i))
        target_path = system_root_path(native_target_path)
        target_path.make_dir(until=system_root_path, readable_by_all=True)
        additional_modules_dir("krrez").copy_to(target_path("krrez"), readable_by_all=True)
        krrez_pth_content += f"{native_target_path}\n"

    target_dist_packages_path = system_root_path("__")
    target_dist_packages_path.make_dir(exist_ok=True, readable_by_all=True)
    target_dist_packages_path("krrez").symlink_to("/usr/local/share/krrez")
    target_dist_packages_path("krrez.pth").write_text(krrez_pth_content)

    if install_krrez_packages:
        python_version = list(system_root_path.glob("usr/lib/python3.*"))[0].name
        target_dist_packages_path = system_root_path(f"usr/local/lib/{python_version}/dist-packages")  # TODO debian specific path?
        for x in system_root_path("__").iterdir():
            x.move_to(target_dist_packages_path(x.name))
        system_root_path("__").rmdir()
