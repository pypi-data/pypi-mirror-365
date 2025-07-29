# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import re
import pathlib
import shlex
import string
import typing as t

import hallyd

import krrez.api.internal
import krrez.flow


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):
    """
    Various kinds of utility functions that are too specialized to integrate them anywhere else, but too useful to
    exclude them.
    """

    def generate_name(self, *, comment: str = "", counter: t.Union[str, type] = "", name_part: t.Optional[str] = None,
                      max_length: int = 16) -> str:
        counters_file = krrez.flow.KRREZ_VAR_DIR("name_counters")

        if not isinstance(counter, str):
            counter = f"{counter.__module__}.{counter.__qualname__}"
        if name_part is None:
            name_part = counter

        with self._lock:
            if counters_file.exists():
                counters = hallyd.bindle.loads(counters_file.read_text())
            else:
                counters = {}

            index = counters.get(counter, 0)
            counters[counter] = index + 1

            counters_file.set_data(hallyd.bindle.dumps(counters))

        sid_alphabet = string.digits + string.ascii_lowercase

        sid = ""

        while not sid or index > 0:
            sid += sid_alphabet[index % len(sid_alphabet)]
            index = index // len(sid_alphabet)

        result = "krz"

        if name_part:
            result += f"_{name_part}"

        result += f"_{sid}"

        if len(result) > max_length:
            raise RuntimeError("unable to generate a new name due to value overflow")

        if comment and (max_length - len(result) >= 2 + min(8, len(comment))):
            result += "__"

            last_was_special = True
            for char in comment.lower():
                if len(result) == max_length:
                    completed = False
                    break
                char_is_special = char not in sid_alphabet
                if char_is_special:
                    char = "" if last_was_special else "_"
                last_was_special = char_is_special
                result += char
            else:
                completed = True

            if not completed:
                result = result[:-1] + "_"

        return result

    def validate_name(self, name: str, *, min_length: int = 1, max_length: int = 100,
                      allowed_first_chars: str = "0-9A-Za-z", allowed_chars: str = "._-",
                      allowed_last_chars: t.Optional[str] = None,
                      including_first_chars: str = "", including_chars: str = "",
                      excluding_first_chars: str = "", excluding_chars: str = "") -> None:

        if len(name) < min_length:
            raise ValueError(f"invalid name {name!r}: must have a length of at least {min_length}")
        if len(name) > max_length:
            raise ValueError(f"invalid name {name!r}: must have a length of at most {max_length}")

        def spat(s):
            return "[" + s.replace('\\', '\\\\').replace(']', '\\]').replace('^', '\\^') + "]"

        if allowed_last_chars is not None:
            if not re.fullmatch(spat(allowed_last_chars), name[-1]):
                raise ValueError(f"invalid name {name!r}: character {name[-1]!r} at position {len(name)} not allowed")

        def pat(i, s1, s2):
            return "|".join([spat(sx) for sx in (s1, "" if (i == 0) else s2) if sx])

        for i, char in enumerate(name):
            this_allowed_pattern = pat(i, allowed_first_chars, allowed_chars)
            this_including_pattern = pat(i, including_first_chars, including_chars)
            this_excluding_pattern = pat(i, excluding_first_chars, excluding_chars)
            if not re.match(f"{this_allowed_pattern}|{this_including_pattern}",
                            char) or re.fullmatch(this_excluding_pattern, char):
                raise ValueError(f"invalid name {name!r}: character {char!r} at position {i+1} not allowed")

    def install_files(self, path: t.Optional[hallyd.fs.TInputPath], base_name: t.Optional[str], *,
                      default_dir_name: str, destination_dir: hallyd.fs.TInputPath,
                      mode: hallyd.fs.TModeSpec = True, owner: hallyd.fs.TOwnerSpec = True,
                      group: hallyd.fs.TOwnerGroupSpec = True, readable_by_all: hallyd.fs.TOptionalFlagSpec = None,
                      executable: hallyd.fs.TOptionalFlagSpec = None,
                      destination_name_converter: t.Optional[t.Callable[[str], str]] = None,
                      before_copy: t.Optional[t.Callable[[hallyd.fs.Path, hallyd.fs.Path], None]] = None,
                      after_copy: t.Optional[t.Callable[[hallyd.fs.Path, hallyd.fs.Path], None]] = None) -> list[krrez.api.Path]:
        result = []

        if destination_name_converter is None:
            def destination_name_converter(s):
                return s

        if before_copy is None:
            def before_copy(*_):
                pass
        if after_copy is None:
            def after_copy(*_):
                pass

        for file, destination_name in self.installable_files(path, base_name,
                                                             default_dir_name=default_dir_name).items():
            destination_file = hallyd.fs.Path(destination_dir, destination_name_converter(destination_name))
            before_copy(file, destination_file)
            file.copy_to(destination_file, mode=mode, owner=owner, group=group, readable_by_all=readable_by_all,
                         executable=executable, exist_ok=True)
            result.append(destination_file)
            after_copy(file, destination_file)

        return result

    def installable_files(self, path: t.Optional[hallyd.fs.TInputPath], base_name: t.Optional[str], *,
                          default_dir_name: str) -> dict[krrez.api.Path, str]:
        if not self._internals.origin_bit:
            if base_name is None:
                raise ValueError("base_name must be specified when called outside of an apply run")
            if not path:
                raise ValueError("path must be specified when called outside of an apply run")

        result = {}
        for file in self._fs(path or self._internals.origin_bit._data_dir, default_dir_name).iterdir():
            result[file] = f"{f'{self._internals.origin_bit.name}.' if base_name is None else base_name}{file.name}"

        return result

    def command_to_cmdline(self, command: "TCommand") -> str:
        if isinstance(command, pathlib.Path):
            command = [command]

        if isinstance(command, str):
            return f"bash -ic {shlex.quote(str(command))}"
        else:
            return " ".join([shlex.quote(str(s)) for s in command])

    _lock = krrez.api.Lock()


TCommand = t.Union[hallyd.fs.TInputPath, str, t.Iterable[t.Union[hallyd.fs.TInputPath, str]]]
