# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`HorizontalBox`.
"""
import klovve


class HorizontalBox(klovve.ui.Piece):
    """
    A horizontal box with child views.
    """

    #: The child views.
    items: list[klovve.ui.View] = klovve.ui.list_property()
