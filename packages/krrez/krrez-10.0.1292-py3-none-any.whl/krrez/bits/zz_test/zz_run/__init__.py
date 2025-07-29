# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import functools
import os
import time
import typing as t
import uuid
import xml.etree.ElementTree

import hallyd

import krrez.api
import krrez.bits.zz_test.zz_run._libvirt
import krrez.bits.zz_test.zz_run._machine
import krrez.bits.zz_test.zz_run._machine_config
import krrez.bits.zz_test.zz_run._network
import krrez.bits.zz_test.zz_run._orbit
import krrez.bits.zz_test.zz_run._utils
import krrez.flow
import krrez.seeding.reseed


# noinspection PyProtectedMember
class Bit(krrez.api.Bit):

    _run_data = krrez.api.ConfigValue(default={}, type=dict[str, t.Any])

    _data_lock = krrez.api.Lock()

    def __init__(self):
        super().__init__()
        self.__network = None

    def __apply__(self):
        self._apply(create=True)

    @property
    def test_id(self) -> str:
        """
        The id for the current test run.

        It will be a new one after resuming from a landmark.
        """
        return (f"{krrez.flow.context_local_unique_id(krrez.flow.Context(self._internals.session.context.path.parent.parent.parent))}"
                f"-{self._internals.session.context.path.name}")

    def machine(self, short_name: str) -> "Machine":
        """
        Return the machine by short name.

        :param short_name: The machine short name.
        """
        return Machine(self, short_name)

    @property
    def all_machines(self) -> list["Machine"]:
        """
        All machines that are currently existing for the current test run.
        """
        return [machine for machine in [self.machine(machine_name) for machine_name in sorted(
            [fp.name for fp in self._machines_dir.iterdir()] if self._machines_dir.exists() else [])]
                if machine.exists]

    def machine_configuration(self, machine_short_name, *, store_afterwards: bool = True
                              ) -> t.ContextManager["krrez.bits.zz_test.zz_run._machine_config._MachineConfiguration"]:
        return krrez.bits.zz_test.zz_run._machine_config.machine_configuration(
            self, machine_short_name, store_afterwards=store_afterwards)

    def seed_machine(self, machine: "Machine") -> None:
        """
        Run the seed procedure for a machine.

        This will happen with the profile data that was configured for this machine, including its seed strategy,
        which will influence the exact behavior of this method.

        Returns after the machine is fully installed and rebooted, but without mounting the data partition.

        :param machine: The machine to seed.
        """
        profile = krrez.bits.zz_test.zz_run._machine_config.profile_for_machine(self, machine.short_name)
        self._log.message.info(f"Starting to create a {machine.short_name!r} test machine with IP address"
                               f" {machine.ip4_address}. This could take an hour or even longer.")

        if isinstance(profile.seed_strategy, krrez.seeding.SeedRemovableSystemDiskDirectly):
            with hallyd.disk.connect_diskimage(machine._disks()[0]) as storage_vol:
                self.__seed_machine__seed(machine, profile, storage_vol)

        else:
            with krrez.bits.zz_test.zz_run._utils.TemporaryStorageStick(self._internals.session) as storage_stick:
                with storage_stick.as_block_device() as storage_stick_block_device:
                    self.__seed_machine__seed(machine, profile, storage_stick_block_device)
                machine.shut_down()
                machine.insert_storage_stick(storage_stick)
                self.__seed_machine__turn_machine_on_and_wait_for_shutdown_incl_reboot(machine)
                machine.unplug_storage_stick(storage_stick)

        self.__seed_machine__turn_machine_on_and_wait_for_shutdown_incl_reboot(machine)
        machine.turn_on()
        machine.exec(["true"])
        machine.exec("echo 'ResolveUnicastSingleLabel=yes' >> /etc/systemd/resolved.conf"
                     " && systemctl restart systemd-resolved")

    def reseed_machine(self, machine: "Machine") -> None:
        """
        Run the re-seed procedure for a machine.

        Returns after the machine is fully reinstalled and rebooted, but without mounting the data partition.

        :param machine: The machine to re-seed.
        """
        with self.machine_configuration(machine.short_name, store_afterwards=False) as machine_config:
            pass
        machine.bit(Bit)._reseed_this_machine(machine_config)

        for _ in range(3):
            while True:
                try:
                    machine.try_exec("true", timeout=30)
                except TimeoutError:
                    break
                time.sleep(3)
            while True:
                try:
                    machine.try_exec("true", timeout=30)
                    break
                except TimeoutError:
                    time.sleep(3)

    @property
    def network(self) -> "Network":
        if not self.__network:
            self.__network = Network(self)
        return self.__network

    def data(self, key: str, default: t.Optional[t.Any] = None) -> t.Optional[t.Any]:
        """
        Return the value for a data key. See also :py:meth:`set_data`.

        :param key: The key.
        :param default: The default (returned if there was no value set before).
        """
        with self._data_lock:
            key_path = self._data_dir(key)
            return hallyd.bindle.loads(key_path.read_text()) if key_path.exists() else default

    def set_data(self, key: str, value: t.Optional[t.Any]) -> None:
        """
        Sets a data key to a value. The value will be available for the current test run and when a new one resumes from
        its landmark. There is also :py:meth:`set_run_data`.

        :param key: The key.
        :param value: The new value.
        """
        with self._data_lock:
            self._data_dir(key).write_text(hallyd.bindle.dumps(value))

    def run_data(self, key: str, default: t.Optional[t.Any] = None) -> t.Optional[t.Any]:
        """
        Return the value for a run_data key. See also :py:meth:`set_run_data`.

        :param key: The key.
        :param default: The default (returned if there was no value set before).
        """
        return self._run_data.value.get(key, default)

    def set_run_data(self, key: str, value: t.Optional[t.Any]) -> None:
        """
        Sets a run_data key to a value. The value will be available for the current test run, but not when a new one
        resumes from its landmark. There is also :py:meth:`set_data`.

        :param key: The key.
        :param value: The new value.
        """
        with self._run_data as x:
            x.value[key] = value

    def _apply(self, *, create: bool) -> None:
        hallyd.cleanup.add_cleanup_task(krrez.bits.zz_test.zz_run._utils.cleanup_run_dir, self._run_dir)
        if create:
            for dir_path in [self._run_dir, self._machines_dir, self._data_dir]:
                dir_path.make_dir(readable_by_all=True)

    @property
    def _run_dir(self) -> t.Optional[krrez.api.Path]:
        if self._internals.session:
            return self._internals.session.path("run")

    @property
    def _machines_dir(self) -> t.Optional[krrez.api.Path]:
        if self._run_dir:
            return self._run_dir("machines")

    @property
    def _data_dir(self) -> t.Optional[krrez.api.Path]:
        if self._run_dir:
            return self._run_dir("data")

    def _reseed_this_machine(self, machine_config):
        krrez.seeding.reseed.run(backup_connection_name=False,
                                 _for_zz_test={"profile_arguments": machine_config.profile_arguments,
                                               "additional_config": machine_config.additional_config})

    def _deserialize_dom(self, s):
        sxml = xml.etree.ElementTree.fromstring(s)
        name = sxml.find("name").text.rpartition("--")[2]
        result = Machine(self, name)
        sxml.find("name").text = full_name = krrez.bits.zz_test.zz_run._utils.machine_full_name(self.test_id, name)
        sxml.find("uuid").text = str(uuid.uuid4())
        sxml.find("devices/interface/mac").set("address", result.mac_address)
        sxml.find("devices/interface/source").set("network", self.network.name)
        sxml.find("devices/filesystem/source").set("dir", str(result.shared_dir_in_host_path))
        sxml.find("os/nvram").text = str(self._fs(result._machine_dir_path("nvram.fd")))
        for xn in sxml.findall("devices/disk"):
            xn.find("source").set("file",
                                  str(result._machine_dir_path(os.path.basename(xn.find("source").get("file")))))
        s = xml.etree.ElementTree.tostring(sxml).decode()
        hallyd.cleanup.add_cleanup_task(krrez.bits.zz_test.zz_run._libvirt.remove_domain, full_name)

        self.network.add_machine(result)
        krrez.bits.zz_test.zz_run._libvirt.define_domain(s)
        return result

    def __seed_machine__turn_machine_on_and_wait_for_shutdown_incl_reboot(self, machine: "Machine") -> None:
        machine.turn_on(shutdown_instead_of_reboot=True)
        machine.exec(["true"])
        while not machine.is_shut_down:
            time.sleep(10)

    def __seed_machine__seed(self, machine: "Machine", profile, target) -> None:
        with self._log.block.debug(f"Seeding medium for test machine {machine.short_name!r}.") as log_block:
            with profile.seed_strategy.seed(profile, target=target, log_block=log_block) as runner:
                runner.ensure_successful()


_Orbit = _orbit.Orbit
Machine = _machine.Machine
Network = _network.Network
