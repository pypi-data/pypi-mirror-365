# SPDX-FileCopyrightText: © 2022 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import site
import typing as t

import hallyd

import krrez.api.internal
import krrez.flow


@krrez.api.internal.usage_does_not_imply_a_dependency
class Bit(krrez.api.Bit):
    """
    File system access.
    """

    @property
    def python_site_modules_dir(self) -> krrez.api.Path:
        return self(site.getsitepackages()[0])

    @property
    def etc_dir(self) -> krrez.api.Path:
        return self("/etc")

    @property
    def krrez_etc_dir(self) -> krrez.api.Path:
        return krrez.flow.KRREZ_ETC_DIR

    @property
    def krrez_var_dir(self) -> krrez.api.Path:
        return krrez.flow.KRREZ_VAR_DIR

    def temp_dir(self, **kwargs) -> t.ContextManager[krrez.api.Path]:
        return krrez.api.Path.temp_dir(**kwargs)

    def home_dir(self, user: t.Optional[str] = None) -> krrez.api.Path:
        return hallyd.fs.Path.home_dir(user)

    def __truediv__(self, other) -> krrez.api.Path:
        return self(other)

    def __call__(self, *paths: hallyd.fs.TInputPath) -> krrez.api.Path:
        return krrez.api.Path("/")(*paths)
