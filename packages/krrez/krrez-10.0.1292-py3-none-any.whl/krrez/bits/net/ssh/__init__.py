# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import time

import krrez.api
import krrez.flow


class Bit(krrez.api.Bit):

    _firewall: krrez.api.IfPicked["krrez.bits.net.firewall.Bit"] # TODO noh is reference to krrez_additionals
    __later: krrez.api.Later["krrez.bits.sys.config.Bit", "krrez.bits.net.ssh.LateBit"]

    def __apply__(self):
        self._packages.install("openssh-server")
        self._internals.context.config.set("net.ssh.available_since", datetime.datetime.now())

        self._fs.etc_dir("ssh/sshd_config.d/krrez.conf").set_data(f"Port {self.port}\n")

        self._services.restart_service("ssh")

        if self._firewall:
            self._firewall.accept_tcp(self.port, include_in_fallback_mode=True)

    @property
    def port(self) -> int:
        return self._internals.context.config.get("net.ssh.port", 22)

class LateBit(krrez.api.Bit):

    __more_deps: krrez.api.Beforehand[krrez.api.IfPicked["krrez.bits.seed.common.ConfirmationBit"],
                                      krrez.api.IfPicked["krrez.bits.sys.data_partition.Bit"],
                                      krrez.api.IfPicked["krrez.bits.net.web.Bit"],
                                      krrez.api.IfPicked["krrez.bits.desktop.environment.Bit"]]

    def __apply__(self):
        available_since = self._internals.context.config.get("net.ssh.available_since")
        available_for = datetime.datetime.now() - available_since
        time.sleep(max(0.0, (datetime.timedelta(minutes=1.5) - available_for).total_seconds()))
