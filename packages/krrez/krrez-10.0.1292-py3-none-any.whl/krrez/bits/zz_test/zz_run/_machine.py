# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import base64
import contextlib
import os
import shlex
import time
import typing as t
import uuid
import xml.etree.ElementTree

import hallyd

import krrez.api
import krrez.bits.sys.packages
import krrez.bits.zz_test.zz_run._libvirt
import krrez.bits.zz_test.zz_run._machine_config
import krrez.bits.zz_test.zz_run._machine_exec
import krrez.bits.zz_test.zz_run._network
import krrez.bits.zz_test.zz_run._utils


# noinspection PyProtectedMember
class Machine:

    def __init__(self, run: "krrez.bits.zz_test.zz_run.Bit", short_name: str):
        self.__run = run
        self.__short_name = short_name
        self.__libvirt_dom__cache = None
        self.__machine_dir = run._machines_dir(self.__short_name)
        os.makedirs(self.__machine_dir, exist_ok=True)

    def bit(self, bit_type: type["_TBit"]) -> "_TBit":
        self.__ensure_created()
        # noinspection PyTypeChecker
        return _BitWrapper(self, self.__run, f"{bit_type.__module__}.{bit_type.__qualname__}")

    @property
    def run(self) -> "krrez.bits.zz_test.zz_run.Bit":
        return self.__run

    @property
    def short_name(self) -> str:
        return self.__short_name

    @property
    def mac_address(self) -> str:
        return self.network.mac_address_for_machine(self)

    @property
    def ip4_address(self) -> str:
        return self.network.ip4_address_for_machine(self)

    @property
    def hostnames(self) -> list[str]:
        return [self.hostname]

    @property
    def hostname(self) -> str:
        return krrez.bits.zz_test.zz_run._machine_config.profile_for_machine(self.__run, self.short_name).hostname

    @property
    def exists(self) -> bool:
        return self.__libvirt_dom is not None

    @property
    def network(self) -> "krrez.bits.zz_test.zz_run.Network":
        return self.__run.network

    @property
    def shared_dir_in_host_path(self) -> krrez.api.Path:
        return self.__machine_dir("share")

    @property
    def shared_dir_in_machine_path(self) -> krrez.api.Path:
        return krrez.api.Path("/mnt/krrez_testing_share")

    def turn_on(self, *, shutdown_instead_of_reboot: bool = False) -> None:
        with self.__change_dom_xml() as xml_dom:
            xml_dom.find("on_reboot").text = "destroy" if shutdown_instead_of_reboot else "restart"
        self.__libvirt_dom.create()

    def insert_storage_stick(self, stick: "krrez.bits.zz_test.zz_run._utils.TemporaryStorageStick") -> None:
        with self.__change_dom_xml() as xml_dom:
            xml_devices = xml_dom.find("devices")
            if len([x for x in xml_devices.findall("disk/source") if x.attrib["file"] == stick.image_path]) > 0:
                raise StorageStickPlugStateError("this stick is already plugged in")
            for potential_disk_device_name in krrez.bits.zz_test.zz_run._utils.potential_disk_device_names():
                if len([x for x in xml_devices.findall("disk/target")
                        if x.attrib["dev"] == potential_disk_device_name]) == 0:
                    target_dev_name = potential_disk_device_name
                    break
            else:
                raise MachineError("out of disk names")
            xml_usbstick = xml.etree.ElementTree.Element("disk", {"type": "file", "device": "disk"})
            xml_usbstick.append(xml.etree.ElementTree.Element("boot", {"order": "1"}))
            xml_usbstick.append(xml.etree.ElementTree.Element("driver", {"name": "qemu", "type": "raw"}))
            xml_usbstick.append(xml.etree.ElementTree.Element("source", {"file": str(stick.image_path)}))
            xml_usbstick.append(xml.etree.ElementTree.Element("target", {"dev": target_dev_name, "bus": "usb"}))
            xml_devices.append(xml_usbstick)

    def unplug_storage_stick(self, stick: "krrez.bits.zz_test.zz_run._utils.TemporaryStorageStick") -> None:
        with self.__change_dom_xml() as xml_dom:
            xml_devices = xml_dom.find("devices")
            for xml_disk in xml_devices.findall("disk"):
                if xml_disk.find("source").attrib["file"] == str(stick.image_path):
                    xml_devices.remove(xml_disk)
                    break
            else:
                raise StorageStickPlugStateError("this stick was not plugged in")

    def exec(self, command: t.Union[list[str], str], *, timeout: float = 60*60*4, cwd: t.Optional[str] = None,
             with_logging: bool = True) -> str:
        res = self.try_exec(command, timeout=timeout, cwd=cwd, with_logging=with_logging)
        if not res.success:
            raise ExecFailedError(command, res.error_message)
        return res.stdout

    def try_exec(self, command: t.Union[list[str], str], *, timeout: float = 60*60*4, cwd: t.Optional[str] = None,
                 with_logging: bool = True) -> "krrez.bits.zz_test.zz_run._machine_exec.ExecutionResult":
        self.__ensure_created()
        if isinstance(command, str):
            command = ["bash", "-c", command]
        command = [str(x) for x in command]
        with contextlib.ExitStack() as stack:
            if with_logging:
                log_block = stack.enter_context(self.__run._log.block.debug(
                    f"Execute on {self.short_name!r}: {command}"))
            cmdqueue_path = self.shared_dir_in_host_path("cmdqueue")
            result = krrez.bits.zz_test.zz_run._machine_exec.exec_on_cmdqueue(cmdqueue_path, command, timeout=timeout,
                                                                              cwd=str(cwd or ""))
            if with_logging:
                log_block.message.debug(f"Return code: {result.returncode}, "
                                        f"Output: {result.stdout}\n{result.stderr}\n{result.error_message}")
            return result

    def put_file(self, *, host_source_path: hallyd.fs.TInputPath, machine_target_path: hallyd.fs.TInputPath) -> None:
        host_source_path, machine_target_path = hallyd.fs.Path(host_source_path), hallyd.fs.Path(machine_target_path)
        temp_name = hallyd.lang.unique_id()
        host_source_path.copy_to(host_temp_target := self.shared_dir_in_host_path(temp_name), readable_by_all=True)
        self.exec(f"cp -ar {shlex.quote(str(self.shared_dir_in_machine_path(temp_name)))}"
                  f" {shlex.quote(str(machine_target_path))}")
        host_temp_target.remove()

    def get_file(self, *, machine_source_path: hallyd.fs.TInputPath, host_target_path: hallyd.fs.TInputPath) -> None:
        machine_source_path, host_target_path = hallyd.fs.Path(machine_source_path), hallyd.fs.Path(host_target_path)
        temp_name = hallyd.lang.unique_id()
        self.exec(f"cp -ar {shlex.quote(str(machine_source_path))}"
                  f" {shlex.quote(str(self.shared_dir_in_machine_path(temp_name)))}")
        (host_temp_target := self.shared_dir_in_host_path(temp_name)).copy_to(host_target_path, readable_by_all=True)
        host_temp_target.remove()

    def download(self, url: str, to_file: t.Optional[str] = None,
                 username: t.Optional[str] = None, password: t.Optional[str] = None) -> t.Optional[bytes]:
        self.bit(krrez.bits.sys.packages.Bit).install("wget")
        wget_result = self.try_exec(["wget", url, "-O", (to_file or "-"),
                                     *([f"--user={username}", f"--password={password}"] if username else [])])
        if wget_result.success:
            return wget_result.bstdout

    @property
    def is_shut_down(self) -> bool:
        self.__ensure_created()
        import libvirt
        return self.__libvirt_dom.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF

    def shut_down(self) -> None:
        self.__ensure_created()
        import libvirt
        with self.__run._log.block.debug("Shutdown machine."):
            if self.__libvirt_dom:
                for i_try in range(6000):  # TODO range(60)  -  as soon as we don't occassionally freeze during shutdown
                    if i_try % 10 == 0:
                        try:
                            self.__libvirt_dom.shutdown()
                        except libvirt.libvirtError:
                            pass
                    if self.is_shut_down:
                        break
                    time.sleep(15)
                if not self.is_shut_down:
                    raise MachineError(f"failed to shutdown machine {self.short_name!r}")

    def reboot(self) -> None:
        self.shut_down()
        self.turn_on()

    @property
    def _machine_dir_path(self) -> krrez.api.Path:
        return self.__machine_dir

    def _serialized_dom(self) -> str:
        return self.__libvirt_dom.XMLDesc(0)

    def _disks(self) -> list[hallyd.fs.Path]:
        with krrez.bits.zz_test.zz_run._machine_config.machine_configuration(
                self.__run, self.short_name, store_afterwards=False) as machine_configuration:
            pass
        result = []
        for disk_index, disk_size_gb in enumerate(machine_configuration.disk_sizes_gb):
            vpath = self.__machine_dir(
                f"disk-{krrez.bits.zz_test.zz_run._utils.potential_disk_device_names()[disk_index]}.img")
            if not vpath.exists():
                hallyd.disk.create_diskimage(vpath, size_gb=disk_size_gb)
            result.append(vpath)
        return result

    @contextlib.contextmanager
    def __change_dom_xml(self) -> t.Generator[xml.etree.ElementTree.Element, None, None]:
        self.__ensure_created()

        dom_xml = self.__libvirt_dom.XMLDesc()
        dom_xml_node = xml.etree.ElementTree.fromstring(dom_xml)

        yield dom_xml_node

        krrez.bits.zz_test.zz_run._libvirt.define_domain(xml.etree.ElementTree.tostring(dom_xml_node,
                                                                                        encoding="unicode"))

    @property
    def __full_name(self) -> str:
        return krrez.bits.zz_test.zz_run._utils.machine_full_name(self.__run.test_id, self.__short_name)

    @property
    def __libvirt_dom(self):
        if not self.__libvirt_dom__cache:
            for libvirt_dom in krrez.bits.zz_test.zz_run._libvirt.all_domains():
                if libvirt_dom.name() == self.__full_name:
                    self.__libvirt_dom__cache = libvirt_dom
                    break

        return self.__libvirt_dom__cache

    def __ensure_created(self) -> None:
        with self.__run._internals.session.context.lock("machine_create", ns=krrez.bits.zz_test.zz_run.Bit):
            if not self.exists:
                self.__create()
                self.__run.network.add_machine(self)

    def __create(self) -> None:
        profile = krrez.bits.zz_test.zz_run._machine_config.profile_for_machine(self.__run, self.short_name)
        with krrez.bits.zz_test.zz_run._machine_config.machine_configuration(
                self.__run, self.short_name, store_afterwards=False) as machine_configuration:
            pass
        hallyd.cleanup.add_cleanup_task(krrez.bits.zz_test.zz_run._libvirt.remove_domain, self.__full_name)

        self._disks()
        self.shared_dir_in_host_path.make_dir(readable_by_all=True, exist_ok=True)

        domain_definition = krrez.bits.zz_test.zz_run._libvirt.AMD64LibvirtDomainDefinition
        if profile.arch == "armhfvirt":
            domain_definition = krrez.bits.zz_test.zz_run._libvirt.ARMHFLibvirtDomainDefinition
        if profile.arch == "arm64virt":
            domain_definition = krrez.bits.zz_test.zz_run._libvirt.ARM64LibvirtDomainDefinition

        krrez.bits.zz_test.zz_run._libvirt.define_domain(domain_definition(
            full_name=self.__full_name,
            memory_gb=machine_configuration.memory_gb,
            network_name=self.__run.network.name,
            mac_address=self.mac_address,
            disk_sizes_gb=machine_configuration.disk_sizes_gb,
            shared_dir_in_host_path=self.shared_dir_in_host_path,
            bootloader="efi" if profile.arch=="x86_64" else "uboot",#TODO
            machine_dir=self.__machine_dir).as_xml())


# noinspection PyProtectedMember
class _BitWrapper:

    def __init__(self, machine: Machine, run: "krrez.bits.zz_test.zz_run.Bit", bit_type_name: str):
        self.__machine = machine
        self.__run = run
        self.__bit_type_name = bit_type_name

    def __getattr__(self, item):
        def func(*args, **kwargs):
            remote_temp_dir = krrez.api.Path(f"/tmp/krrez_test_{uuid.uuid4()}")
            with self.__run._log.block.debug(
                    f"Calling on {self.__machine.short_name}: {self.__bit_type_name}.{item}"
                    f"({', '.join([*[repr(v) for v in args], *[f'{k}={repr(v)}' for k, v in kwargs.items()]])})"
            ) as log_block:
                module_partition = self.__bit_type_name.rpartition(".")
                args_b64 = base64.b64encode(hallyd.bindle.dumps(args).encode())
                kwargs_b64 = base64.b64encode(hallyd.bindle.dumps(kwargs).encode())
                spy = (f"import base64,{module_partition[0]} as mdo,krrez.flow.bit_loader,hallyd,traceback\n"
                       f"with open({str(remote_temp_dir('_'))!r}, 'wb') as f:\n"
                       f" try:\n"
                       f"  iface = krrez.flow.bit_loader.bit_for_secondary_usage(mdo.{module_partition[2]}, "
                       f"                                                        used_by=None)\n"
                       f"  f.write(base64.b64encode(hallyd.bindle.dumps("
                       f"{{'result':iface.{item}("
                       f"*hallyd.bindle.loads(base64.b64decode({args_b64})),"
                       f"**hallyd.bindle.loads(base64.b64decode({kwargs_b64})))}}).encode()))\n"
                       f" except:\n"
                       f"  f.write(base64.b64encode(hallyd.bindle.dumps("
                       f"{{'error':traceback.format_exc()}}).encode()))\n")  # TODO does the error handling really work?
                sspy = shlex.quote(spy)
                output = self.__machine.exec(f"mkdir {shlex.quote(str(remote_temp_dir))}; echo {sspy}|python3")
                if output:
                    log_block.message.debug(output)
                result_dict = hallyd.bindle.loads(base64.b64decode(self.__machine.exec(
                    f"cat {shlex.quote(str(remote_temp_dir))}/_; rm -rf {shlex.quote(str(remote_temp_dir))}",
                    with_logging=False)).decode())
                error = result_dict.get("error", None)
                if error:
                    raise RuntimeError(f"adminapi call failed: {error}")
                result = result_dict["result"]
                log_block.message.debug("Result: " + krrez.bits.zz_test.zz_run._utils.trim_result_log_string(repr(result)))
                return result
        return func


class MachineError(RuntimeError):
    pass


class HostMachineError(MachineError):
    pass


class StorageStickPlugStateError(MachineError):
    pass


class ExecFailedError(MachineError):

    def __init__(self, command: list[str], output: str):
        super().__init__(f"Error in exec {command}: {output}")
        self.command = output.strip()
        self.output = output.strip()


_TBit = t.TypeVar("_TBit", bound=krrez.api.Bit)
