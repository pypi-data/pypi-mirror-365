# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import abc
import os
import shutil
import subprocess
import typing as t
import uuid

import hallyd

import krrez.bits.zz_test.zz_run._utils

try:
    import libvirt
except:
    pass


def define_domain(xml: str) -> "libvirt.virDomain":
    return _libvirt().defineXML(xml)


def define_network(xml: str) -> "libvirt.virNetwork":
    return _libvirt().networkDefineXML(xml)


def all_domains() -> t.Iterable["libvirt.virDomain"]:
    return _libvirt().listAllDomains()


def all_networks() -> t.Iterable["libvirt.virNetwork"]:
    return _libvirt().listAllNetworks()


def remove_network(network_name: str) -> None:
    for nts in _libvirt().listAllNetworks():
        if nts.name() == network_name:
            try:
                nts.destroy()
            except Exception:
                pass
            try:
                nts.undefine()
            except Exception:
                pass


def remove_domain(domain_name: str) -> None:  # TODO
    for dms in _libvirt().listAllDomains():
        if dms.name() == domain_name:
            for _ in range(999999):
                if dms.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
                    break
                try:
                    dms.destroy()
                except Exception:
                    pass
            try:
                dms.undefineFlags(
                    libvirt.VIR_DOMAIN_UNDEFINE_NVRAM | libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
            except Exception:
                pass


_libvirt_conn = None


def _libvirt() -> "libvirt.virConnect":
    global _libvirt_conn
    if not _libvirt_conn:
        _libvirt_conn = libvirt.open("qemu:///system")
    return _libvirt_conn


class LibvirtDomainDefinition(abc.ABC):

    def __init__(self, *, full_name: str, memory_gb: float, mac_address: str, network_name: str,
                 shared_dir_in_host_path: hallyd.fs.Path, disk_sizes_gb: list[float],
                 machine_dir: hallyd.fs.Path, number_cpus: int, bootloader: str):
        self.__full_name = full_name
        self.__memory_gb = memory_gb
        self.__mac_address = mac_address
        self.__network_name = network_name
        self.__shared_dir_in_host_path = shared_dir_in_host_path
        self.__disk_sizes_gb = disk_sizes_gb
        self.__machine_dir = machine_dir
        self.__number_cpus = number_cpus
        self.__bootloader = bootloader

    @property
    def _machine_dir(self) -> hallyd.fs.Path:
        return self.__machine_dir

    def __disks_as_xml(self):
        xml_disks = ""
        for disk_index, disk_size_gb in enumerate(self.__disk_sizes_gb):
            targetdevname = krrez.bits.zz_test.zz_run._utils.potential_disk_device_names()[disk_index]
            vpath = f"{self.__machine_dir}/disk-{targetdevname}.img"
            sbootorder = "<boot order='2'/>" if (disk_index == 0) else ""
            xml_disks += f"""
                <disk type='file' device='disk'>
                    <driver name='qemu' type='raw'/>
                    <source file='{vpath}'/>
                    <backingStore/>
                    <target dev='{targetdevname}' bus='sata'/>
                    {sbootorder}
                </disk>"""
        return xml_disks

    def __bootloader_as_xml(self):
        if self.__bootloader == "efi":
            return (f"<loader readonly='yes' type='pflash'>/usr/share/OVMF/OVMF_CODE_4M.fd</loader>"
                    f"<nvram>{self.__machine_dir}/nvram.fd</nvram>")
        return ""

    @abc.abstractmethod
    def _os_as_xml(self) -> str:
        pass

    @abc.abstractmethod
    def _specific_as_xml(self) -> str:
        pass

    @abc.abstractmethod
    def _emulator(self) -> str:
        pass

    @abc.abstractmethod
    def _domain_type(self) -> str:
        pass

    def as_xml(self):
        return f"""
            <domain type='{self._domain_type()}'>
                <name>{self.__full_name}</name>
                <uuid>{uuid.uuid4()}</uuid>
                <memory unit="b">{int(hallyd.disk.size(gib=self.__memory_gb))}</memory>
                <currentMemory unit="b">{int(hallyd.disk.size(gib=self.__memory_gb))}</currentMemory>
                <vcpu placement='static'>{self.__number_cpus}</vcpu>
                <resource><partition>/machine</partition></resource>
                <os>{self._os_as_xml()}{self.__bootloader_as_xml()}</os>
                {self._specific_as_xml()}
                <clock offset='utc'/>
                <on_poweroff>destroy</on_poweroff>
                <on_crash>destroy</on_crash>
                <devices>
                    <emulator>/usr/bin/qemu-system-{self._emulator()}</emulator>
                    {self.__disks_as_xml()}
                    <interface type='network'>
                        <mac address='{self.__mac_address}'/>
                        <source network='{self.__network_name}'/>
                        <model type='virtio'/>
                    </interface>
                    <controller type='usb' model='qemu-xhci'/>
                    <input type='mouse'/>
                    <input type='keyboard'/>
                    <graphics type='spice' autoport='yes'/>
                    <filesystem type="mount" accessmode="mapped">
                        <source dir="{self.__shared_dir_in_host_path}"/>
                        <target dir="krrez_testing_share"/>
                    </filesystem>
                    <sound model='ich6'>
                        <backend name='null'/>
                    </sound>
                </devices>
            </domain>"""


class AMD64LibvirtDomainDefinition(LibvirtDomainDefinition):

    def __init__(self, **kwargs):
        super().__init__(number_cpus=4, **kwargs)

    def _os_as_xml(self):
        return "<type arch='x86_64' machine='pc-q35-3.1'>hvm</type>"

    def _specific_as_xml(self):
        return (f"""
            <features><acpi/><apic/><vmport state='off'/></features>
            <cpu mode='custom' match='exact' check='full'>
                <model fallback='forbid'>qemu64</model>
                <feature policy='disable' name='vmx'/>
                <feature policy='require' name='svm'/>
                <feature policy='require' name='x2apic'/>
                <feature policy='require' name='hypervisor'/>
                <feature policy='require' name='lahf_lm'/>
            </cpu>"""
        )

    def _emulator(self):
        return "x86_64"

    def _domain_type(self):
        return "kvm"


class _ARMLibvirtDomainDefinition(LibvirtDomainDefinition):

    def __init__(self, **kwargs):
        super().__init__(number_cpus=1, **kwargs)

    def kernelxml(self):
        vpath = self._machine_dir(f"disk-{krrez.bits.zz_test.zz_run._utils.potential_disk_device_names()[0]}.img")

        with hallyd.disk.connect_diskimage(vpath) as devnbd:
            kernelpath, initrdpath, rootpartidx = self.__extract_kernel(devnbd,
                                                                        f"{self._machine_dir}/extractkernel")
            return self._generate_kernelxml(kernelpath, initrdpath, f"root=/dev/sda{rootpartidx} rw")

    @classmethod
    def _generate_kernelxml(cls, kernelpath: t.Optional[str], initrdpath: t.Optional[str],
                            kernelargs: t.Optional[str]) -> str:
        return ((f"<kernel>{kernelpath}</kernel>" if kernelpath else "")
                + (f"<initrd>{initrdpath}</initrd>" if initrdpath else "")
                + (f"<cmdline>{kernelargs}</cmdline>" if kernelargs else ""))

    @classmethod
    def __extract_kernel(cls, devpath, workdirpath):
        kernelpath = initrdpath = rootpartidx = None
        mntpath = f"{workdirpath}/mnt"
        os.makedirs(mntpath, exist_ok=True)
        for partidx in [2, 3]:
            try:
                subprocess.check_call(["mount", f"{devpath}p{partidx}", mntpath])
                if os.path.exists(f"{mntpath}/etc"):
                    rootpartidx = partidx
                for f in sorted(os.listdir(mntpath)):
                    for ff in [f"{mntpath}/{f}", f"{mntpath}/boot/{f}"]:
                        def trycopyfile(fname):
                            if f.startswith(fname) and os.path.isfile(ff):
                                tgtkernelpath = f"{workdirpath}/{fname}"
                                shutil.copyfile(ff, tgtkernelpath)
                                return tgtkernelpath
                        kernelpath = kernelpath or trycopyfile("vmlinuz")
                        initrdpath = initrdpath or trycopyfile("initrd.img")
            except subprocess.CalledProcessError:
                pass
            finally:
                subprocess.call(["umount", f"{devpath}p{partidx}"])
        return kernelpath, initrdpath, rootpartidx

    def _domain_type(self):
        return "qemu"


class ARMHFLibvirtDomainDefinition(_ARMLibvirtDomainDefinition):

    def _os_as_xml(self):
        return f"<type arch='armv7l' machine='virt-2.12'>hvm</type>{self.kernelxml()}"

    def _specific_as_xml(self):
        return "<cpu mode='custom' match='exact' check='none'><model fallback='forbid'>cortex-a15</model></cpu>"

    def _emulator(self):
        return "arm"


class ARM64LibvirtDomainDefinition(_ARMLibvirtDomainDefinition):

    def _os_as_xml(self):
        return f"<type arch='aarch64' machine='virt-3.1'>hvm</type>{self.kernelxml()}"

    def _specific_as_xml(self):
        return "<cpu mode='custom' match='exact' check='none'><model fallback='forbid'>cortex-a57</model></cpu>"

    def _emulator(self):
        return "aarch64"
