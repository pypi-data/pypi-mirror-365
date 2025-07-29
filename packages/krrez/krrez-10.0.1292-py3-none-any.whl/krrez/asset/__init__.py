# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import krrez.api
import krrez.asset.data
import krrez.asset.project_info
import krrez.flow.bit_loader


_TBit = t.TypeVar("_TBit", bound=krrez.api.Bit)


def bit(bit_type: type[_TBit], *, used_by: t.Optional["krrez.api.Bit"] = None,
        skip_installed_check: bool = False) -> _TBit:
    if not skip_installed_check and not krrez.flow.Context().is_bit_installed(bit_type) and not getattr(
            bit_type, "_krrez_do_not_derive_a_dependency", False):
        raise RuntimeError(f"requested bit {krrez.flow.bit_loader.bit_name(bit_type)!r} although it is not installed")
    return krrez.flow.bit_loader.bit_for_secondary_usage(bit_type, used_by=used_by)
