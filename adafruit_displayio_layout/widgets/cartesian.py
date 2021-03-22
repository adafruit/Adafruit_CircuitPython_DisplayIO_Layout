# SPDX-FileCopyrightText: 2021 Jose David Montoya
#
# SPDX-License-Identifier: MIT
"""

`cartesian`
================================================================================
A cartasian plane widget for displaying graphical information.

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

import math
import displayio
import board
import terminalio
from adafruit_displayio_layout.widgets.widget import Widget
import vectorio

try:
    import bitmaptools
except NameError:
    pass  # utilize the blit_rotate_scale function defined herein


class Cartesian(Widget):
    """A cartesian widget.  The origin is set using ``x`` and ``y``.

    :param int x: x position of the plane origin
    :param int y: y position of the plane origin

    :param int display_color: background color to use defaults to black (0x000000)
    :param int width: requested width, in pixels defaults to screen width
    :param int height: requested height, in pixels defaults to screen height

    :param int axes_color: axes lines color defaults to white (0xFFFFFF)
    :param int axes_stroke: axes lines thickness in pixels defaults to 2

    :param int major_tick_stroke: tick lines thickness in pixels dafaults to 1
    :param int major_tick_lenght: tick lines lenght in pixels defaults to 5

    :param int tick_label_font: tick label text font
    :param int tick_label_color: tick label text color

    :param int pointer_radius: pointer radius in pixels defaults to 1
    :param int pointer_color: pointer color defaults to white (0xFFFFFF)

    """

    def __init__(
        self,
        x: int = 10,
        y: int = board.DISPLAY.height - 10,
        display_color=0x000000,
        width: int = board.DISPLAY.width,
        height: int = board.DISPLAY.height,
        axes_color: int = 0xFFFFFF,
        axes_stroke: int = 2,
        tick_color: int = 0xFFFFFF,
        major_tick_stroke: int = 1,
        major_tick_length: int = 5,
        tick_label_font=terminalio.FONT,
        tick_label_color: int = 0xFFFFFF,
        pointer_radius: int = 1,
        pointer_color: int = 0xFFFFFF,
        **kwargs,
    ) -> None:
        # TODO Make axes, separate from data            [X]
        # TODO Replace with drawline/vectorio           [ ]
        # TODO Make a rectangle function                [ ]
        # TODO Include functions to equal space ticks   [ ]
        # TODO Make labels and text                     [ ]
        # TODO Make Styles applicable                   [ ]
        # TODO Animate when overflow                    [ ]

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

        self._usable_width = self._widget_width - 2 * self._margin
        self._usable_height = self._widget_height - 2 * self._margin
        self._tickx_separation = 2 * self._font_width + 2

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
            + self._font_height
            + self._tick_line_height // 2
        )
        self._axesy_bitmap = displayio.Bitmap(self._axesy_width, self._usable_height, 4)
        self._axesy_bitmap.fill(0)

        self._screen_bitmap = displayio.Bitmap(
            self._usable_width, self._usable_height, 3
        )

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
        return font_width, font_height

    def _draw_axes(self):
        y = self._tick_line_height // 2
        bitmaptools.draw_line(self._axesx_bitmap, 0, y, self._usable_width - 1, y, 3)
        bitmaptools.draw_line(
            self._axesy_bitmap,
            self._axesy_width - 1,
            0,
            self._axesy_width - 1,
            self._usable_height - 1,
            3,
        )

    def _draw_ticks(self):
        for i in range(self._margin, self._usable_width, self._tickx_separation):
            if "rotozoom" in dir(bitmaptools):  # if core function is available
                bitmaptools.rotozoom(
                    self._screen_bitmap,
                    ox=i,
                    oy=self._usable_height + self._tick_line_height // 2,
                    source_bitmap=self._tick_bitmap,
                    px=int(self._tick_bitmap.width),
                    py=self._tick_bitmap.height,
                    angle=0.0,  # in radians
                )

        for i in range(self._margin, self._usable_height, self._tickx_separation):
            if "rotozoom" in dir(bitmaptools):  # if core function is available
                bitmaptools.rotozoom(
                    self._screen_bitmap,
                    ox=0,
                    oy=i,
                    source_bitmap=self._tick_bitmap,
                    px=int(self._tick_bitmap.width),
                    py=int(self._tick_bitmap.height / 2),
                    angle=(90 * math.pi / 180),  # in radians
                )

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
