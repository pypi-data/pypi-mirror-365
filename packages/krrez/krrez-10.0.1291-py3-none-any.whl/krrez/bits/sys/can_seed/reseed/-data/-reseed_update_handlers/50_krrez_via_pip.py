# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess
import sys

import hallyd

import krrez.asset.deploy_info


def main(krrez_package_outer_path: hallyd.fs.Path, venv_bin_path: hallyd.fs.Path) -> None:
    if krrez_package_outer_path("krrez/api").exists():  # if krrez itself

        if krrez.asset.deploy_info.is_installed_via_pip:
            krrez_package_outer_path("krrez").remove()
            subprocess.check_call([venv_bin_path("pip3"), "install", "krrez"])


if __name__ == "__main__":
    main(hallyd.fs.Path(sys.argv[1]), hallyd.fs.Path(sys.argv[2]))
