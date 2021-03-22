# SPDX-FileCopyrightText: 2021 Jose David M.
#
# SPDX-License-Identifier: MIT
"""

`cartesian`
================================================================================
A cartesian plane widget for displaying graphical information.

* Author(s): Jose David Montoya

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
import terminalio
import vectorio
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets import rectangle_helper
from adafruit_display_text import bitmap_label

try:
    import bitmaptools
except NameError:
    pass  # utilize the blit_rotate_scale function defined herein
try:
    from typing import Tuple
except ImportError:
    pass


class Cartesian(Widget):
    """A cartesian widget.  The origin is set using ``x`` and ``y``.

    :param int x: x position of the plane origin
    :param int y: y position of the plane origin

    :param int display_color: background color to use defaults to black (0x000000)
    :param int width: requested width, in pixels defaults to 100 pixels
    :param int height: requested height, in pixels defaults to 100 pixels

    :param (int, int) axesx_range: X axes range
    :param (int, int) axesy_range: Y axes range

    :param int axes_color: axes lines color defaults to white (0xFFFFFF)
    :param int axes_stroke: axes lines thickness in pixels defaults to 2

    :param int major_tick_stroke: tick lines thickness in pixels dafaults to 1
    :param int major_tick_length: tick lines length in pixels defaults to 5
    :param List[str] tick_labels: a list of strings for the tick text labels

    :param int tick_label_font: tick label text font
    :param int tick_label_color: tick label text color

    :param int pointer_radius: pointer radius in pixels defaults to 1
    :param int pointer_color: pointer color defaults to white (0xFFFFFF)

    **Quickstart: Importing and using Cartesian**

    Here is one way of importing the `Cartesian` class so you can use it as
    the name ``Plane``:

    .. code-block:: python

        from adafruit_displayio_layout.widgets.cartesian import Cartesian as Plane

    Now you can create a plane at pixel position x=20, y=30 using:

    .. code-block:: python

        my_plane=Plane(x=20, y=30) # instance the plane at x=20, y=30

    Once you setup your display, you can now add ``my_plane`` to your display using:

    .. code-block:: python

        display.show(my_plane) # add the group to the display

    If you want to have multiple display elements, you can create a group and then
    append the plane and the other elements to the group.  Then, you can add the full
    group to the display as in this example:

    .. code-block:: python

        my_plane= Plane(20, 30) # instance the plane at x=20, y=30
        my_group = displayio.Group(max_size=10) # make a group that can hold 10 items
        my_group.append(my_plane) # Add my_plane to the group

        #
        # Append other display elements to the group
        #

        display.show(my_group) # add the group to the display

    """

    def __init__(
        self,
        x: int = 10,
        y: int = 10,
        display_color=0x000000,
        width: int = 100,
        height: int = 100,
        xrange: Tuple[int, int] = (0, 100),
        yrange: Tuple[int, int] = (0, 100),
        axes_color: int = 0xFFFFFF,
        axes_stroke: int = 1,
        tick_color: int = 0xFFFFFF,
        major_tick_stroke: int = 1,
        major_tick_length: int = 5,
        tick_label_font=terminalio.FONT,
        tick_label_color: int = 0xFFFFFF,
        pointer_radius: int = 1,
        pointer_color: int = 0xFFFFFF,
        **kwargs,
    ) -> None:
        # TODO Make axes, separate from data            [√]
        # TODO Replace with drawline/vectorio           [√]
        # TODO Make a rectangle function                [√]
        # TODO Include functions to equal space ticks   [√]
        # TODO Make labels and text                     [√]
        # TODO Make Styles applicable                   [ ]
        # TODO Animate when overflow                    [ ]
        # TODO Add Subticks functionality               [ ]
        # TODO ticks evenly distributed                 [√]
        # TODO Make Ticker lines                        [√]
        # TODO Updater to use local coordinates         [ ]

        super().__init__(**kwargs, max_size=3)
        self._origin_x = x
        self._origin_y = y

        self._margin = 10

        self._display_color = display_color
        self._widget_width = width
        self._widget_height = height

        self._axes_line_color = axes_color
        self._axes_line_thickness = axes_stroke

        self._tick_color = tick_color
        self._tick_line_thickness = major_tick_stroke
        self._tick_line_height = major_tick_length

        self._pointer_radius = pointer_radius
        self._pointer_color = pointer_color

        self._font = tick_label_font
        self._font_color = tick_label_color

        self._font_width = self._get_font_height(self._font, 1)[0]
        self._font_height = self._get_font_height(self._font, 1)[1]

        self._usable_width = self._widget_width
        self._usable_height = self._widget_height

        self._tickx_separation = int(xrange[1] / self._usable_width * 10) + 3
        self._ticky_separation = int(yrange[1] / self._usable_height * 10) + 3

        self._tick_bitmap = displayio.Bitmap(
            self._tick_line_thickness, self._tick_line_height, 3
        )
        self._tick_bitmap.fill(1)

        axesx_height = (
            2
            + self._axes_line_thickness
            + self._font_height
            + self._tick_line_height // 2
        )
        self._axesx_bitmap = displayio.Bitmap(self._usable_width, axesx_height, 4)
        self._axesx_bitmap.fill(0)

        self._axesy_width = (
            2
            + self._axes_line_thickness
            + self._font_width
            + self._tick_line_height // 2
        )
        self._axesy_bitmap = displayio.Bitmap(self._axesy_width, self._usable_height, 4)
        self._axesy_bitmap.fill(0)

        self._screen_bitmap = displayio.Bitmap(
            self._usable_width, self._usable_height, 3
        )
        self._screen_bitmap.fill(0)
        self._screen_palette = displayio.Palette(6)
        self._screen_palette.make_transparent(0)
        self._screen_palette[1] = self._tick_color
        self._screen_palette[2] = self._axes_line_color
        self._screen_palette[3] = 0x990099
        self._screen_palette[4] = 0xFFFFFF
        self._screen_palette[5] = self._display_color

        self._axesx_tilegrid = displayio.TileGrid(
            self._axesx_bitmap,
            pixel_shader=self._screen_palette,
            x=self._origin_x,
            y=self._origin_y + self._usable_height,
        )

        self._axesy_tilegrid = displayio.TileGrid(
            self._axesy_bitmap,
            pixel_shader=self._screen_palette,
            x=self._origin_x - self._axesy_width,
            y=self._origin_y,
        )

        self._screen_tilegrid = displayio.TileGrid(
            self._screen_bitmap,
            pixel_shader=self._screen_palette,
            x=self._origin_x,
            y=self._origin_y,
        )

        self._draw_axes()
        self._draw_ticks()
        self._draw_pointers()
        self.append(self._pointer_vector_shape)
        self.append(self._axesx_tilegrid)
        self.append(self._axesy_tilegrid)
        self.append(self._screen_tilegrid)

    @staticmethod
    def _get_font_height(font, scale):
        if hasattr(font, "get_bounding_box"):
            font_height = int(scale * font.get_bounding_box()[1])
            font_width = int(scale * font.get_bounding_box()[0])
        elif hasattr(font, "ascent"):
            font_height = int(scale * font.ascent + font.ascent)
            font_width = 12
        else:
            font_height = 12
            font_width = 12
        return font_width, font_height

    def _draw_axes(self):
        # Draw x axes line
        if self._axes_line_thickness == 1:
            bitmaptools.draw_line(
                self._axesx_bitmap, 0, 0, self._usable_width - 1, 0, 2
            )
            # Draw y axes line
            bitmaptools.draw_line(
                self._axesy_bitmap,
                self._axesy_width - 1,
                0,
                self._axesy_width - 1,
                self._usable_height - 1,
                2,
            )
        else:
            rectangle_helper(
                0,
                0,
                self._axes_line_thickness,
                self._axesx_bitmap.width - 1,
                self._axesx_bitmap,
                2,
                self._screen_palette,
                True,
            )
            rectangle_helper(
                self._axesy_width - self._axes_line_thickness - 1,
                0,
                self._axesy_bitmap.height,
                self._axes_line_thickness,
                self._axesy_bitmap,
                2,
                self._screen_palette,
                True,
            )

    def _draw_ticks(self):
        # X axes ticks
        tickcounter = 1
        for i in range(
            self._tickx_separation, self._usable_width, self._tickx_separation
        ):
            if tickcounter == 3:
                tickcounter = 0
                shift_label_x = len(str(i)) * self._font_width
                tick_text = bitmap_label.Label(
                    self._font,
                    text=str(i),
                    x=self._origin_x + (i - shift_label_x // 2),
                    y=self._origin_y
                    + self._usable_height
                    + self._axes_line_thickness
                    + self._tick_line_height
                    + self._font_height // 2
                    + 1,
                )
                self.append(tick_text)

            bitmaptools.draw_line(
                self._axesx_bitmap,
                i,
                self._tick_line_height + self._axes_line_thickness,
                i,
                0,
                2,
            )
            tickcounter = tickcounter + 1

        # Y axes ticks
        tickcounter = 0
        for i in range(
            self._usable_height - 1 - self._ticky_separation, 0, -self._ticky_separation
        ):
            if tickcounter == 2:
                tickcounter = 0
                shift_label_x = len(str(self._usable_height - i)) * self._font_width
                tick_text = bitmap_label.Label(
                    self._font,
                    text=str(self._usable_height - i),
                    x=self._origin_x
                    - shift_label_x
                    - self._axes_line_thickness
                    - self._tick_line_height
                    - 2,
                    y=self._origin_y + i + self._font_height,
                )
                self.append(tick_text)

            bitmaptools.draw_line(
                self._axesy_bitmap,
                (self._axesy_width - self._tick_line_height) - 1,
                i,
                self._axesy_width - 1,
                i,
                2,
            )
            tickcounter = tickcounter + 1

    def _draw_pointers(self):
        self._pointer = vectorio.Circle(3)

        self._circle_palette = displayio.Palette(2)
        self._circle_palette.make_transparent(0)
        self._circle_palette[1] = 0xFFFFFF

        self._pointer_vector_shape = vectorio.VectorShape(
            shape=self._pointer,
            pixel_shader=self._circle_palette,
            x=0,
            y=0,
        )

    def update_pointer(self, x: int, y: int):
        """updater_pointer function
        helper function to update pointer in the plane
        :param x: x coordinate in the local plane
        :param y: y coordinate in the local plane
        :return: None
        rtype: None
        """
        self._pointer_vector_shape.x = self._origin_x + x + self._margin
        self._pointer_vector_shape.y = self._origin_y + self._usable_height + y
