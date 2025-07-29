# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import subprocess

import hallyd

import krrez.api
import krrez.bits.seed.steps.disks
import krrez.bits.seed.steps.machine_architecture
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):

    _disks: krrez.bits.seed.steps.disks.Bit
    _machine_architecture: krrez.bits.seed.steps.machine_architecture.Bit

    @property
    def bootloader(self):
        return _bootloader(self._machine_architecture.arch)


class InHostPrepareRawBit(Bit):

    __later: krrez.api.Later["krrez.bits.seed.steps.disks.InHostPrepareRawBit"]

    def __apply__(self):
        bootloader = _bootloader(self._machine_architecture.arch)

        if bootloader == "uboot":
            if self._machine_architecture.arch.uboot_binpath:
                subprocess.check_output(["dd", f"if={self._machine_architecture.arch.uboot_binpath}",
                                         f"of={self._disks.rootfs.value}", "bs=1024", "seek=8"])


class InHostPrepareChrootBit(Bit):

    __more_deps: krrez.api.Beforehand["krrez.bits.seed.steps.system_mounts.InHostPrepareChrootBit"]

    def __apply__(self):
        bootloader = _bootloader(self._machine_architecture.arch)

        if bootloader == "efi":
            try:
                @hallyd.lang.call_now_with_retry(tries=20, interval=10, retry_on=(subprocess.CalledProcessError,))
                def _():
                    subprocess.check_call(["mount", "-t", "efivarfs", "efivarfs",
                                           self._disks.target_path.value("sys/firmware/efi/efivars")])  # fails sometimes
                with self._disks.umounts as x:
                    x.value.append("/sys/firmware/efi/efivars")
            except subprocess.CalledProcessError:
                pass

        elif bootloader == "uboot":
            if self._machine_architecture.arch.uboot_devicetreepath:
                self._machine_architecture.arch.uboot_devicetreepath.copy_to(self._disks.target_path.value(".dtb"),
                                                                             readable_by_all=True)


class InTargetLateBit(Bit):

    def __apply__(self):
        rootfs = self._disks.rootfs.value
        rootfs_removable = self._disks.rootfs_is_removable.value

        arch = self._machine_architecture.arch
        bootloader = _bootloader(self._machine_architecture.arch)

        if bootloader == "uboot":
            self._fs("/boot.txt").write_text(
                'setenv bootargs "root=/dev/mmcblk0p1 rw rootwait panic=10 rootfstype=ext4"\n'
                'load mmc 0:1 $kernel_addr_r vmlinuz\n'
                'load mmc 0:1 $fdt_addr_r /.dtb\n'
                'load mmc 0:1 $ramdisk_addr_r initrd.img\n'
                'bootz ${kernel_addr_r} ${ramdisk_addr_r}:${filesize} ${fdt_addr_r}\n')

            self._packages.install("u-boot-tools")

            subprocess.check_call(["mkimage", "-A", arch.uboot_arch, "-T", "script", "-O", "linux", "-d", "/boot.txt",
                                   "/boot.scr"])

        elif bootloader == "efi":
            self._packages.install(f"grub-efi", "grub2-common", with_recommended=False)

            grub_install_args = ["--no-uefi-secure-boot"]
            if rootfs_removable:
                grub_install_args += ["--no-nvram", "--removable"]

            subprocess.check_call(["grub-install", f"--target={arch.grub_arch}-efi",
                                   *grub_install_args, rootfs])

            self._fs("/etc/default/grub.d/krrez.cfg").write_text("GRUB_DISABLE_OS_PROBER=true\n"
                                                                 "GRUB_TIMEOUT=0\n"
                                                                 "GRUB_TIMEOUT_STYLE=hidden\n")

            subprocess.check_call(["update-grub"])

        else:
            raise ValueError(f"bootloader {self._bootloader.value!r} unsupported")


def _bootloader(arch):
    if arch.name == "x86_64":
        return "efi"
    elif arch.name in ("bananapro", "pinephone", "armhfvirt", "arm64virt"):
        return "uboot"
    else:
        raise ValueError(f"architecture {arch.name!r} is unsupported")
