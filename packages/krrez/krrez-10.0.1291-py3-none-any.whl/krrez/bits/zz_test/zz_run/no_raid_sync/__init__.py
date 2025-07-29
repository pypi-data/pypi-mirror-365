# SPDX-FileCopyrightText: © 2024 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import hallyd

import krrez.api

# performance reasons, also less bloating of disk images


class Bit(krrez.api.Bit):

    __later: krrez.api.Later[krrez.api.IfPicked["krrez.bits.sys.config.Bit"]]

    def __apply__(self):
        with self._services.create_interval_task("krrez_testing_no_raid_sync", _disable_raid_sync) as _:
            _.schedule_by_interval(minutes=1)
            _.start_instantly()


def _disable_raid_sync():
    for sys_md_dir in hallyd.fs.Path("/sys/block").glob("*/md"):
        sys_md_dir("sync_action").write_text("frozen")
        sys_md_dir("resync_start").write_text("none")
        sys_md_dir("sync_action").write_text("idle")
