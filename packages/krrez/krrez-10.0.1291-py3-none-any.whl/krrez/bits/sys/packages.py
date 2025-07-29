# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import hallyd

import krrez.api.internal


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):
    """
    Management of operating system software packages.
    """

    def install(self, *package_names: str, with_recommended: bool = True, aux = None) -> None:
        if package_names:
            aux = aux or {}

            debconf = list(aux.get("debconf") or ())
            if debconf:
                hallyd.subprocess.check_call_with_stdin_string(
                    ["debconf-set-selections"], stdin="\n".join(debconf))

            cmdline = ["apt-get", "install", "--assume-yes"]
            if not with_recommended:
                cmdline.append("--no-install-recommends")
            cmdline += package_names
            hallyd.lang.call_now_with_retry(tries=10, interval=90)(subprocess.check_call, cmdline)

    def uninstall(self, *package_names: str) -> None:
        for package_name in package_names:
            subprocess.call(["apt-get", "remove", "--assume-yes", package_name])

    def pip_install(self, *package_names: str) -> None:
        if package_names:
            self.install("python3-pip")
            cmdline = ["pip3", "install", "--break-system-packages", "--upgrade", *package_names]
            hallyd.lang.call_now_with_retry(tries=10, interval=90)(subprocess.check_call, cmdline)

    def pip_uninstall(self, *package_names: str) -> None:
        if package_names:
            self.install("python3-pip")
            cmdline = ["pip3", "uninstall", *package_names]
            hallyd.lang.call_now_with_retry(tries=10, interval=90)(subprocess.check_call, cmdline)
