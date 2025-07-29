# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import functools
import math
import subprocess
import typing as t

import hallyd

import krrez.api
import krrez.bits.seed.steps.hostname
import krrez.seeding.api


class Bit(krrez.seeding.api.Bit):
    # TODO allow swap partitions in raids, allow multiple EFI partitions (so everything on disk is redundant)
    #      see also https://serverfault.com/questions/1164146/grub2-install-in-multiple-esp-partitions

    _hostname: krrez.bits.seed.steps.hostname.Bit

    _disks = krrez.seeding.api.ConfigValue(type=list["Disk"])
    _raid_partitions = krrez.seeding.api.ConfigValue(type=list["RaidPartition"])
    target_path = krrez.seeding.api.ConfigValue(type=krrez.api.Path)
    _internal_fstab = krrez.seeding.api.ConfigValue(default="", type=str)
    _internal_udevrules = krrez.seeding.api.ConfigValue(type=str)
    umounts = krrez.seeding.api.ConfigValue(default=[], type=list[krrez.api.Path])
    _internal_raid_partitions = krrez.seeding.api.ConfigValue(default=[], type=list[hallyd.disk.RaidSetup])
    rootfs = krrez.seeding.api.ConfigValue(type=krrez.api.Path)
    rootfs_is_removable = krrez.seeding.api.ConfigValue(type=bool)
    _internal_encrypted_swaps = krrez.seeding.api.ConfigValue(default=[], type=list[hallyd.fs.Path])

    def _store_rootfs(self, disk: hallyd.disk.Disk) -> None:
        if not self.rootfs.value:
            with self.rootfs as x:
                x.value = disk.path
            with self.rootfs_is_removable as x:
                x.value = disk.is_removable or not disk.is_disk  # TODO improve


class InHostPrepareBit(Bit):

    def __apply__(self):
        for tool in ["blockdev", "mdadm"]:
            hallyd.subprocess.verify_tool_available(tool)

        disk_intents = hallyd.disk.combine_disks_to_setups(hallyd.disk.host_disks(), self._disks.value)
        for disk_intent in disk_intents:
            self.__handle_diskintent1(disk_intent)
        self._store_rootfs(disk_intents[0].disk)  # just as a fallback e.g. if root fs is on raid

    def __handle_diskintent1(self, diskintent: hallyd.disk.DiskIntent) -> None:
        for partition_entry in hallyd.disk.effective_partition_setup_order(diskintent.setup.partitions):
            partition_setup = partition_entry.partition_setup
            if partition_setup.mountpoint == "/":
                self._store_rootfs(diskintent.disk)


class InHostPrepareRawBit(Bit):

    def __apply__(self):
        disk_intents = hallyd.disk.combine_disks_to_setups(hallyd.disk.host_disks(), self._disks.value)
        self.__stop_old_raid_volumes(disk_intents)

        with self._internal_udevrules as x:
            x.value = "\n".join([disk_intent.udev_rule_for_alias() for disk_intent in disk_intents])

        with self.target_path as x:
            x.value = target_path = self.__new_target_path()

        mountpoints: list[hallyd.disk.Mountpoint] = []

        for disk_intent in disk_intents:
            self.__handle_diskintent(disk_intent, mountpoints, target_path)

        self.__handle_raids(disk_intents, self._raid_partitions.value, mountpoints)

        if "/" not in [x.mountpoint for x in mountpoints]:
            raise ValueError("no root partition specified")

        for mountpointspec in sorted(mountpoints, key=lambda x: x.mountpoint):
            self.__handle_mountpoint(mountpointspec, target_path)

        hallyd.disk.reload_devices()

    def __stop_old_raid_volumes(self, disk_intents):
        for raid_partition in hallyd.disk.host_raid_partitions():
            volume_devs = []

            try:
                volume_devs = [x.path for x in raid_partition.storage_devices]
            except subprocess.CalledProcessError:
                pass

            if my_volume_devs := [volume_dev for volume_dev in volume_devs
                                  if any(disk_intent.setup.do_repartition for disk_intent in disk_intents
                                         if self.__is_on_disk(volume_dev, disk_intent.disk.path))]:
                raid_partition.stop()
                for volume_dev in my_volume_devs:
                    subprocess.call(["mdadm", "--zero-superblock", volume_dev])

    def __is_on_disk(self, volume_dev, disk_dev):
        volume_dev = volume_dev.resolve()
        disk_dev = disk_dev.resolve()
        return str(volume_dev).startswith(str(disk_dev))  # TODO dirty/wrong !

    def __handle_diskintent(self, disk_intent: hallyd.disk.DiskIntent,
                            mountpoints: list[hallyd.disk.Mountpoint], target_path: hallyd.fs.Path) -> None:
        disk_intent.repartition()
        for partition_entry in hallyd.disk.effective_partition_setup_order(disk_intent.setup.partitions):
            partition_setup = partition_entry.partition_setup

            partition = disk_intent.disk.partition(partition_entry.part_no)

            if partition_setup.mountpoint:
                mountpoints.append(partition_setup.mountpoint_spec(partition))

            if partition_setup.do_format and partition_setup.fs_type:
                if partition_setup.use_in_raid:
                    raise ValueError("raid partitions must not have an fs_type")
                partition_setup.make_filesystem(partition.path)

                if partition_setup.fs_type == hallyd.disk.PartitionTypes.ENCRYPTED_SWAP:
                    with self._internal_encrypted_swaps as x:
                        x.value.append(partition.stable_path)

    def __handle_raids(self, disk_intents: list[hallyd.disk.DiskIntent],
                       raid_partition_setups: list[hallyd.disk.RaidPartitionSetup],
                       mountpoints: list[hallyd.disk.Mountpoint]):
        raid_setups = hallyd.disk.raid_setups_from_disk_intents(disk_intents)

        raid_partitions = []
        for raid_partition_setup in raid_partition_setups:
            raid_dev = raid_setups[raid_partition_setup.raid_name].create(do_create=raid_partition_setup.do_create_raid)
            if raid_partition_setup.mountpoint:
                mountpoints.append(raid_partition_setup.mountpoint_spec(hallyd.disk.Partition(raid_dev.path)))
            if raid_partition_setup.do_format and raid_partition_setup.fs_type:
                raid_partition_setup.make_filesystem(raid_dev.path)

        with self._internal_raid_partitions as x:
            x.value = raid_partitions

    def __handle_mountpoint(self, mountpointspec: hallyd.disk.Mountpoint, target_root_path: krrez.api.Path) -> None:
        if mountpointspec.mountpoint:
            with self.umounts as x:
                x.value.append(mountpointspec.mountpoint)
            mountpointspec.mount(prefix=str(target_root_path))
        with self._internal_fstab as x:
            x.value += mountpointspec.fstab_line()

    def __new_target_path(self):
        target_path = krrez.api.Path(f"/mnt/.krrez_seed-{self._internals.session.name}-{hallyd.lang.unique_id()}")
        target_path.make_dir(readable_by_all=True)
        hallyd.cleanup.add_cleanup_task(_cleanup_mount, target_path)
        return target_path


class InHostPrepareChrootBit(Bit):

    def __apply__(self):
        with open(self.target_path.value("etc/fstab"), "a") as f:
            f.write(self._internal_fstab.value)


class InTargetBit(Bit):

    def __apply__(self):
        self._packages.install("cryptsetup", "systemd-cryptsetup", "mdadm")

        if self._internal_udevrules.value:
            with open("/etc/udev/rules.d/61-krrez-diskaliases.rules", "w") as f:
                f.write(self._internal_udevrules.value)

        i_swap = 0
        for encrypted_swap_dev in self._internal_encrypted_swaps.value:
            self._fs("/etc/crypttab").append_data(f"krz_swap{i_swap}    {encrypted_swap_dev}    /dev/urandom    swap")
            self._fs("/etc/fstab").append_data(f"/dev/mapper/krz_swap{i_swap}    none    swap    defaults    0    0")
            i_swap += 1


class InHostOnExitBit(Bit):

    def __apply__(self):
        if not self.target_path.value:
            return

        umounts = [self.target_path.value(krrez.api.Path(umount)) for umount
                   in self.umounts.value]
        for umount_path in reversed(umounts):
            try:
                hallyd.disk.umount(umount_path)
            except Exception:
                self._log.message.warning(f"There were problems with un-mounting '{umount_path}'!")

        subprocess.check_output(["rm", "-rf", "--one-file-system", self.target_path.value])
        if self.target_path.value.exists():
            raise IOError(f"there were problems removing the temporary medium at '{self.target_path.value}'")

        for raiddev in self._internal_raid_partitions.value:
            raiddev.stop()


def _cleanup_mount(path):
    if path.exists():
        subprocess.call(["umount", "-l", path])
        subprocess.check_output(["rm", "-rf", "--one-file-system", path])


size = hallyd.disk.size

Disk = hallyd.disk.DiskSetup
Partition = hallyd.disk.PartitionSetup
RaidPartition = hallyd.disk.RaidPartitionSetup

PartitionTypes = hallyd.disk.PartitionTypes
EfiPartition = hallyd.disk.EfiPartitionSetup
NotEfiPartition = hallyd.disk.NotEfiPartitionSetup


def SwapPartition(*, factor: float = 1, max_size: t.Optional[int] = None, min_size: int = size(gib=3),
                  do_format: bool = True, encrypted: bool = True) -> hallyd.disk.PartitionSetup:
    return hallyd.disk.PartitionSetup(fs_type=PartitionTypes.ENCRYPTED_SWAP if encrypted else PartitionTypes.SWAP,
                                      do_format=do_format,
                                      size=functools.partial(_recommended_swap_size, factor, max_size, min_size))


def FilesystemPartition(*, index: t.Optional[int] = None, fs_type: "hallyd.disk._PartitionType" = PartitionTypes.EXT4,
                        mountpoint: t.Optional[str] = None, label: t.Optional[str] = None, do_format: bool = True,
                        size: hallyd.disk.TPartitionSetupSize = None) -> hallyd.disk.PartitionSetup:
    return hallyd.disk.PartitionSetup(index=index, fs_type=fs_type, mountpoint=mountpoint, label=label,
                                      do_format=do_format, size=size)


def RaidFilesystemPartition(raid_name: str, *, fs_type: "hallyd.disk._PartitionType" = PartitionTypes.EXT4,
                            mountpoint: t.Optional[str] = None, do_format: bool = True,
                            do_create_raid: bool = True) -> hallyd.disk.RaidPartitionSetup:
    return hallyd.disk.RaidPartitionSetup(raid_name, fs_type=fs_type, mountpoint=mountpoint, do_format=do_format,
                                          do_create_raid=do_create_raid)


def RaidStoragePartition(use_in_raid: str, *, index: t.Optional[int] = None,
                         size: "hallyd.disk.TPartitionSetupSize" = None,
                         start_at_mb: t.Optional[float] = None) -> hallyd.disk.PartitionSetup:
    return hallyd.disk.PartitionSetup(use_in_raid=use_in_raid, index=index, size=size, start_at_mb=start_at_mb)


def _recommended_swap_size(factor: float, max_size: t.Optional[int], min_size: int,
                           event: hallyd.disk.PartitionSizingEvent):
    norm_system_ram_size = size(gib=64)
    norm_system_disk_size = size(tib=2)
    result = (norm_system_ram_size / norm_system_disk_size) * factor * event.disk_size
    result = max(min_size, result)
    if max_size is not None:
        result = min(max_size, result)
    return math.ceil(result)
