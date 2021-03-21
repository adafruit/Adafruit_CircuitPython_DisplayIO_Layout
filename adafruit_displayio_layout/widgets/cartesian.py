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
from adafruit_displayio_layout.widgets import _blit_rotate_scale

try:
    import bitmaptools
except NameError:
    pass  # utilize the blit_rotate_scale function defined herein


class Cartesian(Widget):
    """A cartesian widget.  The origin is set using ``x`` and ``y``.

    :param int x: pixel position TODO
    :param int y: pixel position TODO

    :param int width: requested width, in pixels TODO
    :param int height: requested height, in pixels TODO

    """

    def __init__(
        self,
        display_color=0x000000,
        width: int = board.DISPLAY.width,
        height: int = board.DISPLAY.height,
        axes_color=0xFFFFFF,
        axes_stroke=2,
        tick_color=0xFFFFFF,
        major_tick_stroke=1,
        major_tick_length=10,
        tick_label_font=terminalio.FONT,
        tick_label_color=0xFFFFFF,
        **kwargs,
    ):

        super().__init__(**kwargs, max_size=3)

        self._margin = 10

        self._display_color = display_color
        self._display_width = width
        self._display_height = height

        self._axes_line_color = axes_color
        self._axes_line_thickness = axes_stroke

        self._tick_color = tick_color
        self._tick_line_thickness = major_tick_stroke
        self._tick_line_height = major_tick_length
        self._font = tick_label_font
        self._font_color = tick_label_color

        self._font_width = self._get_font_height(self._font, 1)[0]
        self._font_height = self._get_font_height(self._font, 1)[1]

        self._usable_width = self._display_width - self._font_width - 2 * self._margin
        self._usable_height = (
            self._display_height - self._font_height - 2 * self._margin
        )
        self._tickx_separation = 2 * self._font_width + 2

        self._tick_bitmap = displayio.Bitmap(
            self._tick_line_thickness, self._tick_line_height, 3
        )
        self._tick_bitmap.fill(1)

        self._axesx_bitmap = displayio.Bitmap(
            self._axes_line_thickness, self._usable_height, 3
        )
        self._axesx_bitmap.fill(2)

        self._axesy_bitmap = displayio.Bitmap(
            self._usable_width, self._axes_line_thickness, 3
        )
        self._axesy_bitmap.fill(2)

        self._screen_bitmap = displayio.Bitmap(
            self._usable_width, self._usable_height, 6
        )

        self._screen_palette = displayio.Palette(6)
        self._screen_palette[0] = 0x000000
        self._screen_palette[1] = self._tick_color
        self._screen_palette[2] = self._axes_line_color
        self._screen_palette[3] = 0x00FFFF
        self._screen_palette[4] = 0xFFFFFF
        self._screen_palette[5] = self._display_color

        self._screen_tilegrid = displayio.TileGrid(
            self._screen_bitmap,
            pixel_shader=self._screen_palette,
            x=self._margin + self._font_width,
            y=self._margin,
        )

        self._draw_axes()
        self._draw_ticks()
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
        bitmaptools.rotozoom(
            self._screen_bitmap,
            ox=self._margin - 1,
            oy=self._usable_height,
            source_bitmap=self._axesx_bitmap,
            px=self._axesx_bitmap.width,
            py=self._axesx_bitmap.height,
            angle=0.0,  # in radians
        )

        bitmaptools.rotozoom(
            self._screen_bitmap,
            ox=int(self._usable_width - self._margin / 2),
            oy=self._usable_height,
            source_bitmap=self._axesy_bitmap,
            px=self._axesy_bitmap.width,
            py=self._axesy_bitmap.height,
            angle=0.0,
        )

    def _draw_ticks(self):
        for i in range(self._margin, self._usable_width, self._tickx_separation):
            if "rotozoom" in dir(bitmaptools):  # if core function is available
                bitmaptools.rotozoom(
                    self._screen_bitmap,
                    ox=i,
                    oy=self._usable_height,
                    source_bitmap=self._tick_bitmap,
                    px=int(self._tick_bitmap.width / 2),
                    py=self._tick_bitmap.height,
                    angle=0.0,  # in radians
                )
            else:
                _blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
                    destination=self._screen_bitmap,
                    ox=i,
                    oy=0,
                    source=self._tick_bitmap,
                    px=int(self._tick_bitmap / 2),
                    py=self._tick_bitmap.height,
                    angle=0.0,  # in radians
                )

        for i in range(self._margin, self._usable_height, self._tickx_separation):
            if "rotozoom" in dir(bitmaptools):  # if core function is available
                bitmaptools.rotozoom(
                    self._screen_bitmap,
                    ox=self._margin,
                    oy=i,
                    source_bitmap=self._tick_bitmap,
                    px=int(self._tick_bitmap.width / 2),
                    py=int(self._tick_bitmap.height / 2),
                    angle=(90 * math.pi / 180),  # in radians
                )
            else:
                _blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
                    destination=self._screen_bitmap,
                    ox=i,
                    oy=0,
                    source=self._tick_bitmap,
                    px=int(self._tick_bitmap.width / 2),
                    py=int(self._tick_bitmap.height / 2),
                    angle=(90 * math.pi / 180),  # in radians
                )
