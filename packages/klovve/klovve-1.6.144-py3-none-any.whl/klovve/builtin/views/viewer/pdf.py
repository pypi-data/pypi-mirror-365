# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Pdf`.
"""
import pathlib

import klovve.ui.utils


class Pdf(klovve.ui.Piece):
    """
    A PDF viewer.
    """

    #: The PDF source.
    source: pathlib.Path|None = klovve.ui.property()

    @property
    def _fallback_text(self) -> str:
        return klovve.ui.utils.tr("PLEASE_FIND_THE_DOCUMENT_HERE")
