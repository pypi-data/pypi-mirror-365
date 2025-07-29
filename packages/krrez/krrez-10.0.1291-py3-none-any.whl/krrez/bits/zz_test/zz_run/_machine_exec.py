# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import base64
import json
import time
import typing as t

import hallyd


class ExecutionResult:

    def __init__(self, stdout: t.Optional[bytes], stderr: t.Optional[bytes], returncode: int,
                 error_message: t.Optional[str]):
        self.__bstdout = stdout or b""
        self.__bstderr = stderr or b""
        self.__returncode = returncode
        self.__error_message = error_message

    @property
    def success(self) -> bool:
        return self.returncode == 0

    @property
    def answer(self) -> str:
        return self.stdout

    @property
    def stdout(self) -> str:
        return self.bstdout.decode(errors="ignore").strip()

    @property
    def stderr(self) -> str:
        return self.bstderr.decode(errors="ignore").strip()

    @property
    def bstdout(self) -> bytes:
        return self.__bstdout

    @property
    def bstderr(self) -> bytes:
        return self.__bstderr

    @property
    def returncode(self) -> int:
        return self.__returncode

    @property
    def error_message(self) -> t.Optional[str]:
        if self.__error_message:
            return self.__error_message
        if not self.success:
            return f"{self.stdout}\n{self.stderr}"

    def __bool__(self):
        return self.success


def exec_on_cmdqueue(cmdqueue_path: hallyd.fs.Path, command: t.Union[list[str], str], *, timeout: float = 60*60*4,
                     cwd: t.Optional[str] = None) -> ExecutionResult:
    cmd_entry = {"command": command, "cwd": cwd, "timeout_at": time.time() + timeout}
    cmdqueue_path.make_dir(exist_ok=True, preserve_perms=True, mode="a=rwx")
    cmd_entry_path = cmdqueue_path(hallyd.lang.unique_id())
    cmd_entry_path_tmp = hallyd.fs.Path(f"{cmd_entry_path}~")
    cmd_answer_path = hallyd.fs.Path(f"{cmd_entry_path}.answer")
    cmd_entry_path_tmp.write_text(json.dumps(cmd_entry))
    cmd_entry_path_tmp.rename(cmd_entry_path)
    wait_time = 0.05
    begin_time = time.monotonic()
    while not cmd_answer_path.exists():
        if time.monotonic() - begin_time > timeout:
            raise TimeoutError()
        time.sleep(wait_time)
        wait_time = min(5.0, wait_time * 1.2)
    cmd_answer = json.loads(cmd_answer_path.read_text())
    cmd_answer_path.unlink()
    stdout_output = base64.b64decode(cmd_answer["stdout"])
    stderr_output = base64.b64decode(cmd_answer["stderr"])
    returncode = cmd_answer["returncode"]
    error_message = cmd_answer["error_message"]
    return ExecutionResult(stdout=stdout_output, stderr=stderr_output, returncode=returncode,
                           error_message=error_message)
