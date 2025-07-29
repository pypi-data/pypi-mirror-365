# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import krrez.api


class Bit(krrez.api.Bit):

    def __apply__(self):
        self._fs("/etc/adduser.conf").apply_substitutions(
            ("^(.*FIRST_SYSTEM_UID.*)$", "# \\1"),
            ("^(.*LAST_SYSTEM_UID.*)$", "# \\1"),
            ("^(.*FIRST_SYSTEM_GID.*)$", "# \\1"),
            ("^(.*LAST_SYSTEM_GID.*)$", "# \\1"),
            ("^(.*FIRST_UID.*)$", "# \\1"),
            ("^(.*LAST_UID.*)$", "# \\1"),
            ("^(.*FIRST_GID.*)$", "# \\1"),
            ("^(.*LAST_GID.*)$", "# \\1")
        ).append_data(
            "FIRST_SYSTEM_UID=100\n"
            "LAST_SYSTEM_UID=19999\n"
            "FIRST_SYSTEM_GID=100\n"
            "LAST_SYSTEM_GID=19999\n"
            "FIRST_UID=20000\n"
            "LAST_UID=59999\n"
            "FIRST_GID=20000\n"
            "LAST_GID=59999\n",
            preserve_perms=True
        )
