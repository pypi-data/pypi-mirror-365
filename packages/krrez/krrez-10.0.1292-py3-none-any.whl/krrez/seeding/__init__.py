# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Krrez seeding.

This is about mechanisms to apply bits to a target machine, usually by an installation medium that installs a fresh
operation system and all selected bits, according to a chosen profile.
"""
import abc
import contextlib
import copy
import dataclasses
import functools
import subprocess
import time
import traceback
import typing as t

import hallyd

import krrez.api
import krrez.bits.sys.next_boot
import krrez.flow.dialog
import krrez.flow.runner
import krrez.flow.watch
import krrez.flow.writer


class SeedStrategy(abc.ABC):
    """
    Base class for seed strategies. Each seed strategy implements one particular way to install Krrez to a target
    machine.

    This includes the entire procedure, often starting with the creation of an installation medium, and ending with
    a fully installed Krrez system on the target machine. See also the subclasses for a deeper understanding.

    Seeding happens for a chosen :py:class:`Profile`, which specifies what Bits should be
    installed and how things should be set up.
    """

    @contextlib.contextmanager
    def seed(self, profile: "krrez.api.Profile", *, target: t.Optional[krrez.api.Path] = None,
             log_block: t.Optional["krrez.flow.writer.Writer.LogBlock"] = None
             ) -> t.Generator["krrez.flow.watch.Watch", None, None]:
        """
        Executes the seed strategy.

        Note that a seed strategy can (indeed usually does) finish before the target machine is actually installed. It
        usually finishes with the creation of an installation medium, which you have to use to finish the installation
        on the target machine. See also :py:attr:`next_step_message`.

        :param profile: The original profile to seed.
        :param log_block: The engine scope to run in.
        :param target: The target device.
        """
        with self._actual_profile(copy.deepcopy(profile), target) as actual_profile:
            temp_context = krrez.flow.create_blank_context(log_block.session.context if log_block else None)

            for config_key, config_value in actual_profile.to_flow_config_dict().items():
                temp_context.config.set(config_key, config_value)

            with krrez.flow.runner.Engine().start(context=temp_context,
                                                  bit_names=[f"seed.os.{actual_profile.operating_system.name}"],
                                                  log_block=log_block) as watch:
                yield watch
                watch.ensure_successful()

        for _ in range(3):  # TODO cargo cult? how to sync correctly? -> put to hallyd and use this (noh)
            subprocess.check_output(["sync"])

    @property
    @abc.abstractmethod
    def next_step_message(self) -> str:
        """
        Message that describes to the user how to proceed with the installation after :py:meth:`seed` finished.
        """

    @abc.abstractmethod
    def _actual_profile(self, profile: "krrez.api.Profile",
                        target: krrez.api.Path) -> t.Generator["krrez.api.Profile", None, None]:
        """
        Returns a context manager that transforms the original given profile to an internal one. It is a more or less
        direct representation of the original one, depending on the seed strategy, but could be modified in some ways
        that carry the actual implementation for this seed strategy.

        :param profile: The original profile to seed.
        :param target: The target device.
        """


class _IndirectSeedStrategy(SeedStrategy):
    """
    Abstract implementation for indirect seed strategies.

    Those strategies internally consist of two seeds. At first, an installer is seeded to a particular disk. The next
    step is to boot the system from this disk. This will start another seeding to the actual target. The lifetime of the
    installer system ends once the entire installation is done.

    The 1st stage could be seeded to an internal or an external disk, depending on the actual strategy.
    """

    @abc.abstractmethod
    def _stage1_profile(self, profile: "krrez.api.Profile",
                        target: krrez.api.Path) -> t.Generator["krrez.api.Profile", None, None]:
        """
        Returns a context manager that prepares and provides the 1st stage profile.

        :param profile: The original profile to seed.
        :param target: The target device.
        """

    @staticmethod
    def _retry():  # TODO big-retry-loops
        import krrez.bits.seed.steps.krrez_bits as TODO
        krrez.flow.Context().path("installed_bits").remove(not_exist_ok=True)  # TODO nicer
        raise TODO.Retry()

    @contextlib.contextmanager
    def _actual_profile(self, profile, target):
        with self._stage1_profile(profile, target) as stage1_profile:
            profile.indirect__void_installation_medium_during_seed = True
            stage1_profile.krrez_bits += getattr(profile, "stage1_krrez_bits", [])
            # TODO stage1_profile.krrez_on_error_func = self._retry  # TODO big retry
            stage1_profile.first_boot_actions.append(functools.partial(self._first_boot_action, profile))  # TODO big retry
            yield stage1_profile

    @staticmethod
    def _first_boot_action(profile):
        print("\n\n"
              "    Some things need to be prepared on your system.\n\n"
              "    This may take a while. Please be patient.")
        try:
            with _SeedThisMachineDirectly().seed(profile) as runner:
                runner.ensure_successful()
        except Exception:
            traceback.print_exc()
            # TODO more text (and auto reboot after some time?); dedup
            print("\nThe process stopped immaturely due to a fatal error.")
            while True:
                time.sleep(1000)


class _SeedThisMachineDirectly(SeedStrategy):
    """
    Seeds Krrez on this machine in a direct way.

    This is a non-abstract seed strategy, but there is barely a reason to use it directly. It is used internally.
    """

    next_step_message = ""

    @contextlib.contextmanager
    def _actual_profile(self, profile, target):
        yield profile


class SeedRemovableSystemDiskDirectly(SeedStrategy):
    """
    Seeds Krrez by creating a new system disk (SD card for IoT device, ...). You can insert it into the target machine
    and leave it there. It will execute the actual installation on first boot.
    """

    next_step_message = ("The next step is to take your new installation medium, insert it into the target machine, and"
                         " boot from it. This medium will turn into the system medium during installation, so leave it"
                         " attached afterwards.")

    @contextlib.contextmanager
    def _actual_profile(self, profile, target):
        removable_disk_profile = copy.deepcopy(profile)
        removable_disk_profile.disks[0].identify_by = [f"_has_path({str(target)!r})"]
        yield removable_disk_profile


class SeedIndirectlyViaRemovable(_IndirectSeedStrategy):
    """
    Seeds Krrez via a removable boot medium (usb stick, ...). It will be an indirect procedure: On your seed machine,
    an installation medium will be created. You can then insert it into the target machine and boot it from that medium.
    This will execute the actual installation there. Unplug/eject the installation medium afterward.
    """

    next_step_message = ("The next step is to take your new installation medium, insert it into the target machine, and"
                         " boot from it. The installation procedure will void the installation medium, in order to"
                         " avoid the danger of accidentally boot again from it. Remove it after the installation is"
                         " finished.")

    @contextlib.contextmanager
    def _stage1_profile(self, profile, target):
        import krrez.bits.seed.steps.disks as disks
        removable_disk_profile = copy.deepcopy(profile)
        removable_disk_profile.krrez_bits = ["seed.common.ConfirmationBit", "net.ssh"]
        with hallyd.disk.connect_diskimage_buffered(target, buffer_size_gb=8) as target_device:
            removable_disk_profile.disks = [
                disks.Disk(
                    disks.EfiPartition(),
                    disks.Partition(fs_type=disks.PartitionTypes.EXT4, mountpoint="/"),
                    identify_by=[f"_has_path({str(target_device)!r})"]
                )
            ]
            removable_disk_profile.raid_partitions = []
            yield removable_disk_profile


class ReseedThisMachine(_IndirectSeedStrategy):
    """
    Reseeds Krrez on this machine in an indirect way (only supported in some circumstances).

    This strategy is somewhat special AND POTENTIALLY DANGEROUS!

    You can use it on machines that are already seeded Krrez machines. It will install this machine (i.e. your local
    one!) again with the same profile as before.

    This can be useful after a backup, in order to reinstall your system (e.g. to a higher Krrez version).
    """

    next_step_message = ""

    def __init__(self, *, profile_type, profile_data, kept_config,
                 profile_patchers: t.Iterable[t.Callable[["krrez.api.Profile"], None]] = ()):
        super().__init__()
        self.__profile_type = profile_type
        self.__profile_data = profile_data
        self.__kept_config = kept_config
        self.__profile_patchers = tuple(profile_patchers)

    def _actual_profile(self, profile, target):
        profile = self.__profile_type.get(self.__profile_data)
        return super()._actual_profile(profile, target)

    @contextlib.contextmanager
    def _stage1_profile(self, profile: krrez.api.Profile, target):
        for profile_patcher in self.__profile_patchers:
            profile_patcher(profile)

        for kept_config_key, kept_config_value in self.__kept_config.items():
            if kept_config_key not in profile.config:
                profile.config[kept_config_key] = kept_config_value

        yield self._Stage1ProfileGenerator(profile).generate()
        subprocess.check_call(["shutdown", "-r"])

    class _Stage1ProfileGenerator:

        def __init__(self, profile: krrez.api.Profile):
            disks_for_disk_setups = hallyd.disk.find_disks_for_setups(hallyd.disk.host_disks(), profile.disks)
            self.__profile = profile
            self.__stage1_profile = copy.deepcopy(self.__profile)
            self.__host_disks = [disks_for_disk_setups[disk_setup] for disk_setup in self.__profile.disks]

        def generate(self) -> krrez.api.Profile:
            self.__patch_stage1_profile(self.__stage1_profile)
            self.__patch_final_profile(self.__profile)
            self.__patch_working_partition(self.__find_working_partition())
            self.__patch_efi_partitions(list(self.__find_efi_partitions()))
            return self.__stage1_profile

        @dataclasses.dataclass(frozen=True)
        class _PartitionInfo:
            stage1_disk_setup: hallyd.disk.DiskSetup
            stage1_partition_setup: hallyd.disk.PartitionSetup
            final_disk_setup: hallyd.disk.DiskSetup
            final_partition_setup: hallyd.disk.PartitionSetup
            disk_setup_index: int
            partition_setup_index: int
            host_disk: hallyd.disk.Disk
            host_partition: hallyd.disk.Partition

        def __find_working_partition(self) -> "_PartitionInfo":
            for partition in self.__find_partitions(
                    (lambda disk_setup, partition_setup: (partition_setup.fs_type
                                                          in [hallyd.disk.PartitionTypes.ENCRYPTED_SWAP,
                                                              hallyd.disk.PartitionTypes.SWAP]))):
                return partition

            raise RuntimeError("unable to find a reseed working partition")

        def __find_efi_partitions(self) -> t.Iterable["_PartitionInfo"]:
            return self.__find_partitions(
                (lambda disk_setup, partition_setup: (partition_setup.fs_type == hallyd.disk.PartitionTypes.EFI)))

        def __find_partitions(
                self,
                filter_func: t.Callable[[hallyd.disk.DiskSetup, hallyd.disk.PartitionSetup], bool]
        ) -> t.Generator[_PartitionInfo, None, None]:
            for disk_setup_index, disk_setup in enumerate(self.__profile.disks):
                for partition_setup_index, partition_setup in enumerate(disk_setup.partitions):
                    if filter_func(disk_setup, partition_setup):
                        yield self.__partition_by_indexes(disk_setup_index, partition_setup_index)

        def __partition_by_indexes(self, disk_setup_index: int, partition_setup_index: int) -> _PartitionInfo:
            stage1_disk_setup = self.__stage1_profile.disks[disk_setup_index]
            stage1_partition_setup = stage1_disk_setup.partitions[partition_setup_index]
            final_disk_setup = self.__profile.disks[disk_setup_index]
            final_partition_setup = final_disk_setup.partitions[partition_setup_index]
            host_disk = self.__host_disks[disk_setup_index]
            host_partition = hallyd.disk.find_partition_for_setup(host_disk, final_disk_setup, final_partition_setup)
            return self._PartitionInfo(stage1_disk_setup, stage1_partition_setup,
                                       final_disk_setup, final_partition_setup,
                                       disk_setup_index, partition_setup_index,
                                       host_disk, host_partition)

        @staticmethod
        def __patch_stage1_profile(stage1_profile: krrez.api.Profile) -> None:
            stage1_profile.krrez_bits = []

            for raid_partition_setup in stage1_profile.raid_partitions:
                raid_partition_setup.do_create_raid = False
                raid_partition_setup.do_format = False
                raid_partition_setup.mountpoint = None

            all_partition_setups = list(stage1_profile.raid_partitions)
            for disk_setup in stage1_profile.disks:
                disk_setup.do_repartition = False
                all_partition_setups += disk_setup.partitions

            for partition_setup in all_partition_setups:
                if not isinstance(partition_setup, hallyd.disk.PartitionSetup
                                  ) or partition_setup.fs_type != hallyd.disk.PartitionTypes.EFI:
                    partition_setup.mountpoint = None
                partition_setup.do_format = False

        @staticmethod
        def __patch_final_profile(profile: krrez.api.Profile) -> None:
            for raid_partition_setup in profile.raid_partitions:
                raid_partition_setup.do_create_raid = False
            for disk_setup in profile.disks:
                disk_setup.do_repartition = False

        @staticmethod
        def __patch_efi_partitions(efi_partitions: t.Iterable[_PartitionInfo]) -> None:
            for efi_partition in efi_partitions:
                subprocess.check_call(["umount", efi_partition.host_partition.path])
                efi_partition.final_partition_setup.do_format = False

        @staticmethod
        def __patch_working_partition(working_partition: _PartitionInfo) -> None:
            try:
                subprocess.check_output(["swapoff", working_partition.host_partition.path],
                                        stderr=subprocess.STDOUT)
            except Exception:
                pass

            i = 0
            while True:
                try:
                    subprocess.check_output(["swapoff", f"/dev/mapper/krz_swap{i}"],
                                            stderr=subprocess.STDOUT)
                    subprocess.check_output(["dmsetup", "remove", "--retry", f"/dev/mapper/krz_swap{i}"],
                                            stderr=subprocess.STDOUT)
                    i += 1
                except Exception:
                    break

            working_partition.stage1_partition_setup.do_format = True
            working_partition.stage1_partition_setup.mountpoint = "/"
            working_partition.stage1_partition_setup.fs_type = hallyd.disk.PartitionTypes.EXT4

            working_partition.final_partition_setup.do_format = False


class SeedAct(abc.ABC):

    def __init__(self, *, profile: krrez.api.Profile, target_device: krrez.api.Path):
        self.__profile = profile
        self.__target_device = target_device

    @property
    def _target_device(self):
        return self.__target_device

    @abc.abstractmethod
    def _begin(self):
        pass

    @abc.abstractmethod
    def _start_creating_installation_medium(self, watch: "krrez.flow.watch.Watch"):
        pass

    @abc.abstractmethod
    def _installation_medium_created(self, seed_user, seed_strategy):
        pass

    @abc.abstractmethod
    def _start_finishing(self):
        pass

    @abc.abstractmethod
    def _watch_finishing(self, watch: "krrez.flow.watch.Watch"):
        pass

    @abc.abstractmethod
    def _done(self, *, finish_from_here: bool, unknown: bool):
        pass

    def seed(self) -> None:
        seed_user = self.__profile.seed_user

        self._begin()

        with self.__profile.seed_strategy.seed(self.__profile, target=self.__target_device) as runner:
            self._start_creating_installation_medium(runner)
            runner.ensure_successful()

        import subprocess, time;time.sleep(4);subprocess.call(["losetup", "-d", "/dev/loop77"])  # TODO WEG!!!!

        finish_from_here = self._installation_medium_created(seed_user, self.__profile.seed_strategy)
        if finish_from_here:
            self._start_finishing()
            connection_target = hallyd.net.SshConnection(self.__profile.hostname, port=22, user=seed_user.username,
                                                              password=seed_user.password)
            while not connection_target.is_alive():
                time.sleep(60)
            finished = False
            last_seen = time.monotonic()
            while not finished:
                try:
                    remote_root_path = krrez.flow.Context.DEFAULT_ROOT_PATH  # TODO
                    with _RemoteContext(connection_target, remote_root_path) as remote_context:
                        remote_sessions = remote_context.get_sessions()
                        if len(remote_sessions) == 0:
                            raise RuntimeError("no remote session yet")
                        remote_session = remote_sessions[-1]
                        with krrez.flow.watch.Watch(remote_session) as finish_from_here_reader:
                            self._watch_finishing(finish_from_here_reader)  # TODO
                            last_seen = time.monotonic()
                            finish_from_here_reader.wait()
                        finished = True
                except hallyd.net.AccessDeniedError:
                    finished = True
                except hallyd.net.CouldNotConnectError:
                    if time.monotonic() - last_seen > 120:
                        self._done(finish_from_here=False, unknown=True)
                        return
                    time.sleep(10)
#                    finished = True
                except Exception:  # TODO
                    time.sleep(1)

        self._done(finish_from_here=finish_from_here, unknown=False)


class _RemoteContext(krrez.flow.Context):

    def __init__(self, connection: hallyd.net.Connection, root_path: krrez.api.Path):
        self.__tempdir = krrez.flow.create_blank_context()._locals_path()
        super().__init__(self.__tempdir)
        self.__connection = connection
        self.__remote_root_path = root_path

    def _interaction_request_fetcher_for_session(self, session, provider):
        ssession = krrez.flow.Session.by_name(session.name, context=krrez.flow.Context(self.__remote_root_path))
        return krrez.flow.dialog._InteractionRequestFetcher.plug_into_hub(
            krrez.flow.writer._ipc_dialog_hub_path(ssession.path), self.__connection, provider=provider)

    def __enter__(self):
        self.__connection.mount(self.__remote_root_path, self.__tempdir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.__connection.umount(self.__tempdir)
        except Exception:
            pass  # TODO
