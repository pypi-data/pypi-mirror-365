# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import krrez.api
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _arch = krrez.seeding.api.ConfigValue(type=str)

    @property
    def arch(self) -> "_Arch":
        return self.__get_arch(self._arch.value)

    class _Arch:

        def __init__(self, name, *, additionalpackages: list[str], debarch: str, qemuarch: str,
                     grub_arch: str = "",
                     uboot_arch: str = "",
                     uboot_devicetreepath: t.Optional[krrez.api.Path] = None,
                     uboot_binpath: t.Optional[krrez.api.Path] = None):
            self.name = name
            self.additional_packages = additionalpackages
            self.debian_arch = debarch
            self.qemu_arch = qemuarch
            self.uboot_arch = uboot_arch
            self.grub_arch = grub_arch
            self.uboot_devicetreepath = uboot_devicetreepath
            self.uboot_binpath = uboot_binpath

    def __get_arch(self, archname: str) -> _Arch:
        archs = (self._Arch("x86_64", additionalpackages=["linux-image-amd64"], debarch="amd64", qemuarch="x86_64",
                            grub_arch="x86_64"),
                 self._Arch("bananapro", additionalpackages=["linux-image-armmp"], debarch="armhf", qemuarch="arm",
                            uboot_arch="arm", uboot_devicetreepath=self._data_dir("bananapro/sun7i-a20-bananapro.dtb"),
                            uboot_binpath=self._data_dir /"bananapro/u-boot-sunxi-with-spl.bin"),
                 self._Arch("pinephone", additionalpackages=["initramfs-tools"], debarch="arm64", qemuarch="aarch64",
                            uboot_arch="arm64", uboot_binpath=self._data_dir("pinephone/u-boot-sunxi-with-spl.bin")),
                 self._Arch("armhfvirt", additionalpackages=["initramfs-tools", "linux-image-armmp"], debarch="armhf",
                            qemuarch="arm", uboot_arch="arm"),
                 self._Arch("arm64virt", additionalpackages=["initramfs-tools", "linux-image-arm64"], debarch="arm64",
                            qemuarch="aarch64", uboot_arch="arm64"))
        archname = archname or archs[0].name
        for arch in archs:
            if arch.name == archname:
                return arch
        raise ValueError(f"machine architecture unsupported: {archname}")


class InTargetBit(Bit):

    def __apply__(self):
        self._packages.install(*self.arch.additional_packages)
