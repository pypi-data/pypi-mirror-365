# SPDX-FileCopyrightText: © 2023 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import functools
import json
import os
import typing as t

import hallyd

import krrez.asset.project_info
import krrez.bits.seed.steps.seed_user
import krrez.bits.zz_test.zz_run

# This code implements the part of the reseeding procedure that happens after the code updating. It runs in the NEW
# version and environment. It can mostly be changed freely, but it needs to be able to understand the reseed data coming
# from the OLD version of the early part of the procedure and needs to be available in a fixed location!


def _run(from_version: int, serialized_reseed_data: str) -> None:
    """
    Executed internally by `krrez_reseed` as a new process, after the source update happened, in order to continue
    the reseeding procedure in the code of the new Krrez version.

    :param from_version: The Krrez major version of the original system.
    :param serialized_reseed_data: Serialized dictionary with some information. It comes from the reseed procedure
                                   code of the OLD Krrez version!
    """
    this_version = int(krrez.asset.project_info.version.split(".")[0])
    if not (9 <= from_version <= this_version):
        raise RuntimeError(f"your original version of Krrez ({from_version}) is not supported to be reseeded"
                           f" towards the target version ({this_version})")

    reseed_data = _patch_reseed_data(from_version, hallyd.bindle.loads(
        json.dumps(_patch_raw_reseed_data(from_version, json.loads(serialized_reseed_data)))))

    profile_type = reseed_data["profile_type"]
    profile_data = reseed_data["profile_data"]
    kept_config = reseed_data["kept_config"]
    profile_patchers = []

    if for_zz_test := reseed_data.get("for_zz_test"):
        profile_arguments = for_zz_test["profile_arguments"]
        additional_config = for_zz_test["additional_config"]
        profile_patchers.append(functools.partial(krrez.bits.zz_test.zz_run._machine_config.patch_profile_for_machine,
                                                  profile_type, profile_arguments, additional_config))
    else:
        seed_user_password = krrez.bits.seed.steps.seed_user.generate_password()
        profile_patchers.append(functools.partial(_profile_patcher__seed_user_password, seed_user_password))
        print(f"Please write down the following credentials somewhere. They are only valid during"
              f" installation.\n"
              f"     User name: seed  /  Password: {seed_user_password}\n\n")   # TODO dedup string; TODO hardcoded username
        input("Press Enter to continue.")

    with krrez.seeding.ReseedThisMachine(profile_type=profile_type, profile_data=profile_data, kept_config=kept_config,
                                         profile_patchers=profile_patchers).seed(None) as runner:
        runner.ensure_successful()


def _patch_raw_reseed_data(from_version: int, raw_reseed_data: dict[str, t.Any]) -> dict[str, t.Any]:
    """
    Patch the reseed data from the `from_version` version to the current version.

    :param from_version: The Krrez major version of the original system.
    """
    return raw_reseed_data


def _patch_reseed_data(from_version: int, reseed_data: dict[str, t.Any]) -> dict[str, t.Any]:
    """
    Patch the system to be able to reseed from the `from_version` version to the current version.

    :param from_version: The Krrez major version of the original system.
    """
    return reseed_data


def _profile_patcher__seed_user_password(seed_user_password: str, profile):
    if profile.seed_user:
        profile.seed_user.password = seed_user_password


from_version = int(os.environ["KRREZ_RESEED_FROM_VERSION"])
serialized_reseed_data = os.environ["KRREZ_RESEED_DATA"]

_run(from_version, serialized_reseed_data)
