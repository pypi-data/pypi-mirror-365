#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import base64
import json
import pathlib
import subprocess
import threading
import time
import traceback
import typing as t

import hallyd


class Proxy:

    def __init__(self, shared_path: hallyd.fs.Path):
        self.__shared_path = shared_path
        self.__cmdqueue_path = shared_path("cmdqueue")

    def run(self) -> "t.Never":
        self.__mount_shared()
        last_hot = 0
        while True:
            if self.__check_cmdqueue():
                last_hot = time.monotonic()
            last_hot_duration = time.monotonic() - last_hot
            for last_hot_duration_min, sleep_time in reversed([(-1, 0.01), (5, 0.1), (60, 1), (3*60, 10)]):
                if last_hot_duration_min <= last_hot_duration:
                    time.sleep(sleep_time)
                    break

    def __check_cmdqueue(self) -> bool:
        hot = False
        for cmd_path in self.__cmdqueue_path.iterdir():
            if cmd_path.name.endswith("~") or cmd_path.name.endswith(".answer"):
                continue
            cmd_entry = json.loads(cmd_path.read_text())
            cmd_path.unlink()   # TODO MOVE TO LATER ?!?! OR HOW TO BE MORE CRASH RESISTANT?!
            if time.time() <= cmd_entry["timeout_at"]:
                threading.Thread(target=self.__run_cmd,
                                 args=(cmd_entry["command"],
                                       cmd_entry["cwd"] or "/",
                                       cmd_path.with_name(f"{cmd_path.name}.answer")),
                                 daemon=True, name="Command Thread").start()
            hot = True
        return hot

    def __run_cmd(self, command: list[str], cwd, answer_path: pathlib.Path) -> None:
        stdout = b""
        stderr = b""
        returncode = -1
        error_message = None
        try:
            cmd_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
            stdout = cmd_result.stdout
            stderr = cmd_result.stderr
            returncode = cmd_result.returncode
        except IOError:
            error_message = traceback.format_exc()
        answer_path_tmp = pathlib.Path(f"{answer_path}~")
        answer_path_tmp.write_text(json.dumps({"stdout": base64.b64encode(stdout).decode(),
                                               "stderr": base64.b64encode(stderr).decode(),
                                               "returncode": returncode, "error_message": error_message}))
        answer_path_tmp.rename(answer_path)

    def __mount_shared(self):
        self.__shared_path.make_dir(exist_ok=True, until="/", readable_by_all=True)
        if not self.__shared_path.is_mount():
            subprocess.check_call(["mount", "-t", "9p", "-o", "posixacl,trans=virtio", "krrez_testing_share", self.__shared_path])
        self.__cmdqueue_path.make_dir(exist_ok=True, readable_by_all=True)


if __name__ == "__main__":
    time.sleep(25)#TODO weg
    Proxy(hallyd.fs.Path("/mnt/krrez_testing_share")).run()
