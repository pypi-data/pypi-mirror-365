# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Slider`.
"""
import klovve


class Slider(klovve.ui.Piece):
    """
    A slider.
    """

    #: The current value.
    value: float = klovve.ui.property(initial=0)

    #: The minimum value.
    min_value: float = klovve.ui.property(initial=0)

    #: The maximum value.
    max_value: float = klovve.ui.property(initial=1)

    #: The value step size.
    value_step_size: float = klovve.ui.property(initial=0.1)

    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))

    def __init_object__(self):
        klovve.effect.activate_effect(self.__fix_value, owner=self)

    def __fix_value(self):
        self.value = round((self.value - self.min_value)
                           / self.value_step_size) * self.value_step_size + self.min_value
