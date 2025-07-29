# SPDX-FileCopyrightText: © 2024 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import binascii
import math
import socket
import typing as t


_CHARS = "\u2580\u2581\u2584\u2594\u2596\u2597\u2598\u259a\u259d\u259e"


def avatar(machine_hostname: t.Optional[str] = None, *, length: int = 3, chars: t.Iterable[str] = _CHARS) -> str:
    if machine_hostname is None:
        machine_hostname = socket.getfqdn()

    hash_func, hash_range = binascii.crc32, 2 ** 32

    chars = list(chars)
    char_count = len(chars)
    target_range = char_count ** length

    hash = hash_func(machine_hostname.encode())
    hash_value = math.floor(hash * target_range / hash_range)

    return "".join([chars[(hash_value // (char_count ** i)) % char_count] for i in range(length)])
