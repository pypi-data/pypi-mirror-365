# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import hallyd

import krrez.bits.zz_test.zz_run
import krrez.flow.bit_loader
import krrez.flow.logging
import krrez.flow.writer


class Orbit:

    @staticmethod
    def install_machine(context_path: hallyd.fs.TInputPath, session_name: str, log_block_path: str,
                        machine_short_name: str) -> None:
        outer_run = Orbit.__outer_run(context_path, session_name, log_block_path)
        install_bit = krrez.flow.bit_loader.bit_by_name(f"zz_test.zz_profiles.{machine_short_name}.SeedBit")()
        install_bit._internals.initialize_as_secondary(outer_run)
        install_bit.__apply__()

    @staticmethod
    def reseed_machine(context_path: hallyd.fs.TInputPath, session_name: str, log_block_path: str,
                       machine_short_name: str) -> None:
        outer_run = Orbit.__outer_run(context_path, session_name, log_block_path)
        outer_run.reseed_machine(outer_run.machine(machine_short_name))

    @staticmethod
    def __outer_run(context_path: hallyd.fs.TInputPath, session_name: str,
                    log_block_path: str) -> "krrez.bits.zz_test.zz_run.Bit":
        outer_session = krrez.flow.Session.by_name(session_name, context=krrez.flow.Context(context_path))
        outer_run = krrez.bits.zz_test.zz_run.Bit()
        log_block = krrez.flow.writer.Writer.LogBlock(is_root=True, message="", path=log_block_path, aux_name="",
                                                      severity=krrez.flow.logging.Severity.INFO, session=outer_session)
        outer_run._internals.prepare_apply(outer_session, log_block, None)
        return outer_run
