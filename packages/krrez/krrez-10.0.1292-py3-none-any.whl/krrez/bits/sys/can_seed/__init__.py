# SPDX-FileCopyrightText: © 2024 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import krrez.api


class Bit(krrez.api.Bit):

    def __apply__(self):
        self._packages.install("debootstrap", "dosfstools")


"""
TODO big retrying loops

scenarios:
- A: seed a memory card (A1), then insert into a machine and boot into installation (A2)
  - A1: no retry needed
  - A2: out-of-scope; maybe later
- B: seed a usb stick (B1), then boot target machine into seed (B2) and installation (B3)
  - B1: no retry needed
  - B2: easy
  - B3: like krrez_reseed.py but without all the updating
- C: reseed a machine of scenario A by preparation step (C1) and seed step (C2) and installation (C3)
  - C1: no retry needed
  - C2: easy
  - C3: like B3
"""
