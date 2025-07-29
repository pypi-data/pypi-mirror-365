# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import os
import shlex
import subprocess
import sys
import typing as t

import hallyd

import krrez.bits.seed.common
import krrez.bits.seed.os.debian
import krrez.bits.seed.steps.disks
import krrez.bits.seed.steps.machine_architecture
import krrez.bits.sys.config
import krrez.flow.runner
import krrez.flow.ui
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):  # TODO debootstrap sometimes create wget logs in working dir

    _disks: krrez.bits.seed.steps.disks.Bit
    _common: krrez.bits.seed.common.Bit
    _machine_architecture: krrez.bits.seed.steps.machine_architecture.Bit

    _debian_mirror_server = krrez.seeding.api.ConfigValue(type=t.Optional[str])
    _operating_system = krrez.seeding.api.ConfigValue(type="krrez.bits.seed.os.debian.OperatingSystem")


class InHostPrepareBit(Bit):

    def __apply__(self):
        hallyd.subprocess.verify_tool_available("debootstrap")

        if self._machine_architecture.arch.name != os.uname()[4]:
            hallyd.subprocess.verify_tool_available(f"qemu-{self._machine_architecture.arch.qemu_arch}-static")


class InHostBuildRawBit(Bit):  # TODO zz only works if x--host.krz point to local ip on the test host !!!

    def __apply__(self):
        debian_arch = self._machine_architecture.arch.debian_arch
        with self._fs.temp_dir() as temp_dir:
            subprocess.check_call(["debootstrap", f"--arch={debian_arch}", "--include=python3", "--foreign",
                                   self._operating_system.value.version_name, self._disks.target_path.value,
                                   *filter(None, (self._debian_mirror_server.value,))], cwd=temp_dir)


class InHostBuildSystemBit(Bit):

    def __apply__(self):
        target_path = self._disks.target_path.value
        logfile_path = target_path("debootstrap/debootstrap.log")

        try:
            subprocess.check_call(["chroot", target_path, "/bin/bash", "-c", "/debootstrap/debootstrap --second-stage"])
        except Exception:
            if os.path.exists(logfile_path):
                with open(logfile_path, "r") as f:
                    self._log.message.debug(f.read())
            raise


class InHostChrootBit(Bit):

    def __apply__(self):
        in_target_temp_context_path = self._common._in_target_temp_context_path.value
        in_target_bits = self.bit_names_for_stage(krrez.seeding.api.Stage.IN_TARGET)
        in_target_late_bits = self.bit_names_for_stage(krrez.seeding.api.Stage.IN_TARGET_LATE)

        python_code = (f"import {__name__}\n"
                       f"{__name__}.{InHostChrootBit._apply_bits.__qualname__}"
                       f"({str(in_target_temp_context_path)!r}, {in_target_bits!r}, {in_target_late_bits!r})\n")

        subprocess.check_call([
            "unshare", "--uts", "chroot", self._disks.target_path.value, "/bin/bash", "-c",
            f"export DEBIAN_FRONTEND=noninteractive"
            f" && apt-get install --assume-yes"
            f"     python3-pip util-linux mdadm dosfstools debootstrap libncursesw6 systemd-timesyncd"
            f" && pip3 install --break-system-packages -r"
            f"     $(dirname $(realpath $(which krrez)))/runtime-requirements.txt"
            f" && (echo {shlex.quote(python_code)} | python3)"
        ], stdout=sys.stderr)

    @staticmethod
    def _apply_bits(context_path, in_target_bits, in_target_late_bits):
        for bits in (in_target_bits, in_target_late_bits):
            with krrez.flow.runner.Engine().start(context=krrez.flow.Context(context_path),
                                                  bit_names=bits) as session_watch:
                session_watch.ensure_successful()


# TODO linux stores core dumps (in cwd or somewhere)? security risk? resource waste? disable core dumps?
