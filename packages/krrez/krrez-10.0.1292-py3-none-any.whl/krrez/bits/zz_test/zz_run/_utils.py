# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import string
import typing as t

import hallyd

import krrez.flow


def cleanup_run_dir(run_dir_path: hallyd.fs.Path) -> None:
    if not run_dir_path.parent.exists():
        raise RuntimeError("not available at the moment")
    run_dir_path.remove(not_exist_ok=True)


def machine_full_name(test_id: str, machine_short_name: str) -> str:
    return f"krrez-test--{test_id}--{machine_short_name}"


def trim_result_log_string(s: str, max_len: int = 1000) -> str:
    split_str = " [⋯] "
    if isinstance(s, bytes):
        s = s.decode(errors="replace")
    if len(s) > max_len:
        s = s[:int((max_len-len(split_str))/2)] + split_str + s[-int((max_len-len(split_str))/2):]
    return s


def potential_disk_device_names() -> list[str]:
    return [f"sd{letter}" for letter in string.ascii_lowercase]


class TemporaryStorageStick:

    def __init__(self, session: krrez.flow.Session):
        self.__image_dir_path = session.path("temp_storage_sticks")
        self.__image_path = None

    @property
    def image_path(self) -> hallyd.fs.Path:
        if not self.__image_path:
            raise RuntimeError("this action is only valid inside the with-context of this object")
        return self.__image_path

    def as_block_device(self) -> t.ContextManager[hallyd.fs.Path]:
        return hallyd.disk.connect_diskimage(self.__image_path)

    def __enter__(self):
        self.__image_dir_path.make_dir(exist_ok=True, readable_by_all=True)
        self.__image_path = self.__image_dir_path(hallyd.lang.unique_id())
        hallyd.disk.create_diskimage(self.__image_path, size_gb=8)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__image_path.unlink()
        self.__image_path = None
