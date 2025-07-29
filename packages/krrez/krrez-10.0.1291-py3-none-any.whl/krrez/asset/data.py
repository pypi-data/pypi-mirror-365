# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import hallyd


_static_files_dir = hallyd.fs.Path(__file__).parent("_static")

krrez_png_32px = _static_files_dir("krrez.32.png")
krrez_png_64px = _static_files_dir("krrez.64.png")
krrez_png_128px = _static_files_dir("krrez.128.png")
krrez_png_256px = _static_files_dir("krrez.256.png")
krrez_png_512px = _static_files_dir("krrez.512.png")


def readme_pdf(culture: str) -> hallyd.fs.Path:
    for culture in (culture, "en"):
        if (readme_pdf := _static_files_dir(f"README/{culture}.pdf")).exists():
            return readme_pdf
