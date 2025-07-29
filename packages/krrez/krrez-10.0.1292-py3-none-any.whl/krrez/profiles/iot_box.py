# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import krrez.api
import krrez.bits.seed.os.debian
import krrez.bits.seed.steps.disks
import krrez.bits.seed.steps.keyboard
import krrez.bits.seed.steps.networking
import krrez.bits.seed.steps.seed_user
import krrez.seeding

p = krrez.bits.seed.steps


class Profile(krrez.api.Profile):

    is_hidden = True

    def __init__(self, *, hostname: str, arch: str, krrez_bits: list[str], config: dict[str, t.Any]):
        super().__init__(
            hostname=hostname,
            disks=[p.disks.Disk(
                p.disks.EfiPartition(),
                p.disks.FilesystemPartition(mountpoint="/", size=p.disks.size(gib=10)),
                p.disks.FilesystemPartition(),
                p.disks.SwapPartition(),
                identify_by=["is_disk", "not is_removable"], name="krrezdisk1"
            )],
            raid_partitions=[],
            network_interfaces=[p.networking.NetworkInterface("e*", p.networking.ConnectIp4ByDHCP())],
            krrez_bits=[
                "net.ssh",
                *krrez_bits
            ],
            arch=arch, operating_system=krrez.bits.seed.os.debian.OperatingSystem("trixie"),
            keyboard=p.keyboard.Keyboard(layout="us"), locale="en_US", timezone="Etc/UTC",
            seed_strategy=krrez.seeding.SeedRemovableSystemDiskDirectly(),
            seed_user=p.seed_user.SeedUser(),
            config={
                "sys.data_partition.impl.luks.device": "/dev/krrezdisk1p3",
                **config
            },
            drivers=[]
        )
