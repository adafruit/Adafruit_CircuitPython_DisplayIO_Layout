# SPDX-FileCopyrightText: 2021 Jose David M.
#
# SPDX-License-Identifier: MIT
"""

`equalizer`
================================================================================
A equalizer widget for displaying sound information.

* Author(s): Jose David M.

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# pylint: disable=too-many-lines, too-many-instance-attributes, too-many-arguments
# pylint: disable=too-many-locals, too-many-statements

import displayio
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets import rectangle_helper

try:
    from typing import Tuple
except ImportError:
    pass


class Equalizer(Widget):
    """An equalizer widget.  The origin is set using ``x`` and ``y``.

    :param int x: x position of the plane origin
    :param int y: y position of the plane origin

    :param int background_color: background color to use defaults to black (0x000000)
    :param int width: requested width, in pixels.
    :param int height: requested height, in pixels.

    :param (int, int) yrange: Y axes range. Defaults to (0, 100)

    :param int bar_line_color: axes lines color defaults to white (0xFFFFFF)
    :param int bar_line_thickness: axes lines thickness in pixels defaults to 2

    :param int horiz_margin: horizontal margins in pixels. Defaults to 10

    :param int number_bars: number of bars to display. Defaults to 1


    **Quickstart: Importing and using Equalizer**

    Here is one way of importing the `Equalizer` class so you can use it as
    the name ``Equal``:

    .. code-block:: python

        from adafruit_displayio_layout.widgets.cartesian import Equalizer as Equal

    Now you can create an equalizer at pixel position x=20, y=30 using:

    .. code-block:: python

        my_equalizer=Equal(x=20, y=30) # instance the equalizer at x=20, y=30

    Once you setup your display, you can now add ``my_equalizer`` to your display using:

    .. code-block:: python

        display.show(my_equalizer) # add the group to the display

    If you want to have multiple display elements, you can create a group and then
    append the plane and the other elements to the group.  Then, you can add the full
    group to the display as in this example:

    .. code-block:: python

        my_equalizer= Equal(20, 30) # instance the equalizer at x=20, y=30
        my_group = displayio.Group(max_size=10) # make a group that can hold 10 items
        my_group.append(my_equalizer) # Add my_equalizer to the group

        #
        # Append other display elements to the group
        #

        display.show(my_group) # add the group to the display

    """

    def __init__(
        self,
        background_color: int = 0x000000,
        yrange: Tuple[int, int] = (0, 100),
        bar_line_color: int = 0xFFFFFF,
        bar_line_thickness: int = 2,
        horiz_margin: int = 10,
        number_bars: int = 1,
        bar_width: int = 10,
        bars_distance: int = 3,
        **kwargs,
    ) -> None:

        super().__init__(**kwargs, max_size=3)

        self._bar_line_thickness = bar_line_thickness
        self._background_color = background_color

        self._bar_line_color = bar_line_color

        if bar_line_thickness not in range(1, 4):
            print("tick length must be 1-10 pixels. Defaulting to 2")
            self._bar_line_thickness = 2
        else:
            self._bar_line_thickness = bar_line_thickness

        if self.width < 42:
            print("Equalizer minimum width is 40. Defaulting to 40")
            self._width = 40

        self._number_bars = number_bars
        self._horiz_margin = horiz_margin
        self._bar_width = bar_width
        self._bar_distance = bars_distance

        self._yrange = yrange
        self._normy = (self._yrange[1] - self._yrange[0]) / 100
        self._valuey = self.height / 100
        self._factory = 100 / (self._yrange[1] - self._yrange[0])

        self._screen_bitmap = displayio.Bitmap(self.width, self.height, 5)
        self._screen_bitmap.fill(5)
        self._screen_palette = displayio.Palette(6)
        self._screen_palette.make_transparent(0)
        self._screen_palette[1] = 0xFFFFFF
        self._screen_palette[2] = self._bar_line_color
        self._screen_palette[3] = 0x990099
        self._screen_palette[4] = 0xFFFFFF
        self._screen_palette[5] = self._background_color

        self._hor_bar_setup()

        self._screen_tilegrid = displayio.TileGrid(
            self._screen_bitmap,
            pixel_shader=self._screen_palette,
            x=0,
            y=0,
        )

        self.append(self._screen_tilegrid)

    def _hor_bar_setup(self):
        total_width = self._number_bars * (
            2 * self._bar_line_thickness + self._bar_width
        ) + ((self._number_bars + 1) * 2)
        if total_width > self.width:
            print("Equalizer setup could not be display. Adjusting bar widths")
            self._bar_width = (
                self.width
                - self._number_bars * (2 * self._bar_line_thickness)
                + ((self._number_bars + 1) * 2)
            ) // self._number_bars

        widths_bars = self._number_bars * self._bar_width
        width_free = self.width - widths_bars
        separation = width_free // (self._number_bars + 1)
        x_local = separation
        for _ in range(self._number_bars):
            rectangle_helper(
                x_local,
                self.height - (self.height // 2),
                self.height // 2,
                self._bar_width,
                self._screen_bitmap,
                2,
                self._screen_palette,
            )
            x_local = x_local + separation + self._bar_width
            print(x_local)
