# SPDX-FileCopyrightText: 2021 Jose David M.
#
# SPDX-License-Identifier: MIT
"""

`cartesian`
================================================================================
A cartesian plane widget for displaying graphical information.

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
import terminalio
import vectorio
from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets import rectangle_helper

try:
    import bitmaptools
except NameError:
    pass
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

    :param int tick_label_font: tick label text font
    :param int font_color: font color

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
            display_color=0x000000,
            xrange: Tuple[int, int] = (0, 100),
            yrange: Tuple[int, int] = (0, 100),
            axes_color: int = 0xFFFFFF,
            axes_stroke: int = 1,
            tick_color: int = 0xFFFFFF,
            major_tick_stroke: int = 1,
            major_tick_length: int = 5,
            tick_label_font=terminalio.FONT,
            font_color: int = 0xFFFFFF,
            pointer_radius: int = 1,
            pointer_color: int = 0xFFFFFF,
            subticks: bool = False,
            **kwargs,
    ) -> None:
        # TODO Make axes, separate from data            [√]
        # TODO Replace with drawline/vectorio           [√]
        # TODO Make a rectangle function                [√]
        # TODO Include functions to equal space ticks   [√]
        # TODO Make labels and text                     [√]
        # TODO Make Styles applicable                   [√]
        # TODO Animate when overflow                    [ ]
        # TODO Add Subticks functionality               [√]
        # TODO ticks evenly distributed                 [√]
        # TODO Make Ticker lines                        [√]
        # TODO Updater to use local coordinates         [√]

        super().__init__(**kwargs, max_size=3)

        self._display_color = display_color

        self._axes_line_color = axes_color
        self._axes_line_thickness = axes_stroke

        self._tick_color = tick_color
        self._tick_line_thickness = major_tick_stroke
        self._tick_line_height = major_tick_length

        self._pointer_radius = pointer_radius
        self._pointer_color = pointer_color

        self._font = tick_label_font
        self._font_color = font_color

        self._font_width = self._get_font_height(self._font, 1)[0]
        self._font_height = self._get_font_height(self._font, 1)[1]

        self._xrange = xrange
        self._normx = (self._xrange[1] - self._xrange[0]) / 100
        self._valuex = self.width / 100
        self._factorx = 100 / (self._xrange[1] - self._xrange[0])

        self._yrange = yrange
        self._normy = (self._yrange[1] - self._yrange[0]) / 100
        self._valuey = self.height / 100
        self._factory = 100 / (self._yrange[1] - self._yrange[0])

        self._tick_bitmap = displayio.Bitmap(
            self._tick_line_thickness, self._tick_line_height, 3
        )
        self._tick_bitmap.fill(1)

        self._subticks = subticks

        axesx_height = (
                2
                + self._axes_line_thickness
                + self._font_height
                + self._tick_line_height // 2
        )

        self._axesx_bitmap = displayio.Bitmap(self.width, axesx_height, 4)
        self._axesx_bitmap.fill(0)

        self._axesy_width = (
                2
                + self._axes_line_thickness
                + self._font_width
                + self._tick_line_height // 2
        )

        self._axesy_bitmap = displayio.Bitmap(self._axesy_width, self.height, 4)
        self._axesy_bitmap.fill(0)

        self._screen_bitmap = displayio.Bitmap(self.width, self.height, 5)
        self._screen_bitmap.fill(5)
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
            x=0,
            y=self.height,
        )

        self._axesy_tilegrid = displayio.TileGrid(
            self._axesy_bitmap,
            pixel_shader=self._screen_palette,
            x=-self._axesy_width,
            y=0,
        )

        self._screen_tilegrid = displayio.TileGrid(
            self._screen_bitmap,
            pixel_shader=self._screen_palette,
            x=0,
            y=0,
        )

        self._draw_axes()
        self._draw_ticks()

        self.append(self._axesx_tilegrid)
        self.append(self._axesy_tilegrid)
        self.append(self._screen_tilegrid)

        self._update_line = True

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
            bitmaptools.draw_line(self._axesx_bitmap, 0, 0, self.width - 1, 0, 2)
            # Draw y axes line
            bitmaptools.draw_line(
                self._axesy_bitmap,
                self._axesy_width - 1,
                0,
                self._axesy_width - 1,
                self.height - 1,
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
        # ticks definition
        ticks = [10, 30, 50, 70, 90]
        subticks = [20, 40, 60, 80, 100]
        # X axes ticks
        for i in range(10, 100, 10):
            text_tick = str(round(self._xrange[0]) + round(i * self._normx))
            text_dist = int(self._valuex * i)
            if i in ticks:
                shift_label_x = len(text_tick) * self._font_width
                tick_text = bitmap_label.Label(
                    self._font,
                    color=self._font_color,
                    text=text_tick,
                    x=text_dist - (shift_label_x // 2),
                    y=self.height
                      + self._axes_line_thickness
                      + self._tick_line_height
                      + self._font_height // 2
                      + 1,
                )
                self.append(tick_text)
                bitmaptools.draw_line(
                    self._axesx_bitmap,
                    text_dist,
                    self._tick_line_height + self._axes_line_thickness,
                    text_dist,
                    self._axes_line_thickness,
                    1,
                )
            if self._subticks:
                if i in subticks:
                    bitmaptools.draw_line(
                        self._axesx_bitmap,
                        text_dist,
                        self._tick_line_height // 2 + self._axes_line_thickness,
                        text_dist,
                        self._axes_line_thickness,
                        1,
                    )

        # Y axes ticks
        for i in range(10, 100, 10):
            text_tick = str(round(self._yrange[0]) + round(i * self._normy))
            text_dist = int(self._valuey * i)
            if i in ticks:
                shift_label_x = len(text_tick) * self._font_width
                tick_text = bitmap_label.Label(
                    self._font,
                    color=self._font_color,
                    text=text_tick,
                    x=-shift_label_x
                      - self._axes_line_thickness
                      - self._tick_line_height
                      - 2,
                    y=0 + self.height - text_dist,
                )
                self.append(tick_text)

                bitmaptools.draw_line(
                    self._axesy_bitmap,
                    self._axesy_width
                    - self._axes_line_thickness
                    - self._tick_line_height
                    - 1,
                    text_dist,
                    self._axesy_width - 1 - self._axes_line_thickness,
                    text_dist,
                    1,
                )

            if self._subticks:
                if i in subticks:
                    bitmaptools.draw_line(
                        self._axesy_bitmap,
                        self._axesy_width - 1 - self._tick_line_height // 2,
                        text_dist,
                        self._axesy_width - 1,
                        text_dist,
                        1,
                    )

    def _draw_pointers(self, x, y):
        self._pointer = vectorio.Circle(3)
        self._circle_palette = displayio.Palette(2)
        self._circle_palette.make_transparent(0)
        self._circle_palette[1] = self._pointer_color

        self._pointer_vector_shape = vectorio.VectorShape(
            shape=self._pointer,
            pixel_shader=self._circle_palette,
            x=x,
            y=y,
        )
        self.append(self._pointer_vector_shape)

    def update_pointer(self, x: int, y: int):
        """updater_pointer function
        helper function to update pointer in the plane
        :param int x: x coordinate in the local plane
        :param int y: y coordinate in the local plane
        :return: None
        rtype: None
        """
        local_x = int((x - self._xrange[0]) * self._factorx)
        local_y = int((self._yrange[0] - y) * self._factory) + self.height

        if local_x >= 0 or local_y <= 100:
            if self._update_line:
                self._draw_pointers(local_x, local_y)
                self._update_line = False
            else:
                self._pointer_vector_shape.x = local_x
                self._pointer_vector_shape.y = local_y

    def _set_plotter_line(self):
        self.plot_line_point = list()

    def update_line(self, x: int, y: int):
        """updater_line function
        helper function to update pointer in the plane
        :param int x: x coordinate in the local plane
        :param int y: y coordinate in the local plane
        :return: None
        rtype: None
        """
        local_x = int((x - self._xrange[0]) * self._factorx)
        local_y = int((self._yrange[0] - y) * self._factory) + self.height
        if x < self._xrange[1] and y < self._yrange[1]:
            if local_x > 0 or local_y < 100:
                if self._update_line:
                    self._set_plotter_line()
                    self.plot_line_point.append((local_x, local_y))
                    self._update_line = False
                else:
                    bitmaptools.draw_line(
                        self._screen_bitmap,
                        self.plot_line_point[-1][0],
                        self.plot_line_point[-1][1],
                        local_x,
                        local_y,
                        1,
                    )

    def set_widget_style(self, new_style: str) -> None:
        """set_widget_style function
        Allows to set the widget style
        :param str new_style: style for the widget
        :return: None
        """
        # import would change after library packaging
        # pylint: disable=import-outside-toplevel
        from adafruit_styles import get_hex
        from adafruit_styles import styles

        colorset = styles.THEME
        self._pointer_color = get_hex(colorset[new_style]["TEXT"])
        self._font_color = get_hex(colorset[new_style]["TEXT"])
        self._draw_ticks()