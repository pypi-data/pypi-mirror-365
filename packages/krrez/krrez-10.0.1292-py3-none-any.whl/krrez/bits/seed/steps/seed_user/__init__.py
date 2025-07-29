# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import random
import subprocess
import typing as t

import hallyd

import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _seed_user = krrez.seeding.api.ConfigValue(type=t.Optional["SeedUser"])


class InTargetBit(Bit):

    def __apply__(self):
        self._packages.install("sudo")

        seed_user = self._seed_user.value
        if seed_user:
            # TODO use self._system_users ?!
            self._packages.install("openssl")
            hash = subprocess.check_output(["openssl", "passwd", "-6", seed_user.password]).decode().strip()
            subprocess.check_call(["useradd", seed_user.username, "--create-home", "-s", "/bin/bash",
                                   "-p", hash])

            with open("/etc/sudoers.d/seed", "w") as f:
                f.write("%seed ALL=NOPASSWD: ALL\n")


@hallyd.lang.with_friendly_repr_implementation()
class SeedUser:
    """
    A seed user specification.
    """

    def __init__(self, username: str = "seed", *, password: t.Optional[str] = None):
        self.username = username
        self.password = generate_password() if (password is None) else password


# TODO remove seed user after installation


def generate_password() -> str:
    return ''.join(random.choices("abcdefghijkmnopqrstuvwxyz23456789", k=7))
