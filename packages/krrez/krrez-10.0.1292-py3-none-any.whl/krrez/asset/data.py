# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import hallyd


_static_files_dir = hallyd.fs.Path(__file__).parent("_static")

krrez_png = _static_files_dir("krrez.png")


def readme_pdf(culture: str) -> hallyd.fs.Path:
    for culture in (culture, "en"):
        if (readme_pdf := _static_files_dir(f"README/{culture}.pdf")).exists():
            return readme_pdf
