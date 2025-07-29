# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import grp
import pwd
import subprocess
import typing as t

import hallyd

import krrez.api.internal


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):
    """
    Management of operating system users and groups.
    """

    __more_deps: krrez.api.Beforehand["krrez.bits.sys.increase_system_users_range.Bit"]

    def change_user(self, user_name: str, *, home_dir: t.Optional[t.Union[bool, hallyd.fs.TInputPath]] = None,
                    shell: t.Optional[str] = None) -> None:
        """
        Change a user.

        It will only make changes it you set some keyword arguments.

        :param user_name: The name of the user to change.
        :param home_dir: The home directory path.
        :param shell: The user's shell.
        """
        if home_dir is True:
            raise ValueError("home_dir=True is not allowed for change_user")

        opts = []

        if shell is not None:
            opts += ["--shell", shell]

        if home_dir is not None:
            opts += ["--home", home_dir or "/bin"]

        subprocess.check_call(["usermod", *opts, user_name])

    def create_user(self, user_name: t.Optional[str] = None, *, home_dir: t.Union[bool, hallyd.fs.TInputPath] = False,
                    allow_login: bool = False, ugid: t.Optional[int] = None, with_container_support: bool = False,
                    comment: t.Optional[str] = None, assign_to_group: t.Optional[str] = None,
                    shell: str = "/bin/sh", password: t.Optional[str] = None) -> str:
        """
        Create a new user.

        Returns the user name.

        :param user_name: The user name. If :code:`None`, it gets automatically generated.
        :param home_dir: The home directory path. Set to :code:`True` for an automatic path. By default, no home
                         directory is created.
        :param allow_login: Whether this user shall be allowed to log in.
        :param ugid: If set, use this value as uid and gid.
        :param with_container_support: Shortcut for some other parameters to enable container support.
        :param comment: The user comment. Will be used for an automatically determined user name.
        :param assign_to_group: Group names for additional group memberships.
        :param shell: The user's shell. Only relevant if login is allowed.
        :param password: The account password.
        """
        # TODO usermod later on automatically (by sys.containers) instead of with_container_support?!
        user_name = user_name or self._helpers.generate_name(comment=comment, counter=Bit, name_part="sys",
                                                             max_length=self._NAME_MAX_LENGTH)
        self.validate_name(user_name)
        if with_container_support:
            home_dir = home_dir or True
            allow_login = True
        opts = [
            "--system",
            *([f"--gid", assign_to_group] if assign_to_group else ["--user-group"]),
            "--shell", shell if allow_login else "/sbin/nologin",
            "--comment", f"krrez system user{'; ' if comment else ''}{comment or ''}",
            *(["--add-subids-for-system"] if with_container_support else []),
        ]
        if home_dir:
            opts += ["--create-home"]
            if home_dir is not True:
                opts += ["--home-dir", home_dir]
        else:
            opts += ["--home-dir", "/bin"]
        if ugid is not None:
            opts += ["--uid", str(ugid)]
        subprocess.check_call(["useradd", *opts, user_name])

        if password is not None:
            hallyd.subprocess.check_call_with_stdin_string(["chpasswd"], stdin=f"{user_name}:{password}")

        return user_name

    def create_group(self, group_name: str, *, gid: t.Optional[int] = None) -> str:  # TODO  auto naming like for users
        """
        Create a new group.

        Returns the group name.

        :param group_name: The group name.
        :param gid: If set, use this value as gid.
        """
        opts = ["--system"]
        if gid is not None:
            opts += ["--gid", str(gid)]
        subprocess.check_call(["groupadd", *opts, group_name])
        return group_name

    def assign_to_group(self, *, user: str, group: str) -> None:
        """
        Assign a user to a group (additionally to its former assignments).

        :param user: The user to add.
        :param group: The group to add the user to.
        """
        subprocess.check_call(["usermod", "--append", "--groups", group, user])

    def delete_user(self, user: str) -> None:
        subprocess.check_call(["userdel", user])

    def delete_group(self, group: str) -> None:
        subprocess.check_call(["groupdel", group])

    def validate_name(self, name: str) -> None:
        self._helpers.validate_name(name, max_length=Bit._NAME_MAX_LENGTH)

    def primary_group_of_user(self, name: str) -> str:
        return grp.getgrgid(pwd.getpwnam(name).pw_gid).gr_name

    _NAME_MAX_LENGTH = 31
