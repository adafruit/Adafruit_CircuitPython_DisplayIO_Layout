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
from adafruit_display_text import bitmap_label
import vectorio
from adafruit_displayio_layout.widgets.widget import Widget

try:
    import bitmaptools
except ImportError:
    pass

try:
    from typing import Any, List, Optional, Tuple
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class Cartesian(Widget):
    """A cartesian widget.  The origin is set using ``x`` and ``y``.

    :param int x: x position of the plane origin
    :param int y: y position of the plane origin

    :param int background_color: background color to use defaults to black (0x000000)
    :param int width: requested width, in pixels.
    :param int height: requested height, in pixels.

    :param (int, int) xrange: X axes range. Defaults to (0, 100)
    :param (int, int) yrange: Y axes range. Defaults to (0, 100)

    :param int axes_color: axes lines color defaults to white (0xFFFFFF)
    :param int axes_stroke: axes lines thickness in pixels defaults to 2

    :param int major_tick_stroke: tick lines thickness in pixels defaults to 1
    :param int major_tick_length: tick lines length in pixels defaults to 5

    :param terminalio.FONT tick_label_font: tick label text font
    :param int font_color: font color. Defaults to white (0xFFFFFF)

    :param int pointer_radius: pointer radius in pixels defaults to 1
    :param int pointer_color: pointer color. Defaults to white (0xFFFFFF)

    :param bool subticks: inclusion of subticks in the plot area. Default to False

    :param int nudge_x: movement in pixels in the x direction to move the origin.
     Defaults to 0
    :param int nudge_y: movement in pixels in the y direction to move the origin.
     Defaults to 0

    :param bool verbose: print debugging information in some internal functions. Default to False

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

        display.root_group = my_plane # add the group to the display

    If you want to have multiple display elements, you can create a group and then
    append the plane and the other elements to the group.  Then, you can add the full
    group to the display as in this example:

    .. code-block:: python

        my_plane= Plane(20, 30) # instance the plane at x=20, y=30
        my_group = displayio.Group() # make a group
        my_group.append(my_plane) # Add my_plane to the group

        #
        # Append other display elements to the group
        #

        display.root_group = my_group # add the group to the display


    **Summary: Cartesian Features and input variables**

    The `cartesian` widget has some options for controlling its position, visible appearance,
    and scale through a collection of input variables:

        - **position**: ``x``, ``y``, ``anchor_point``, ``anchored_position`` and
          ``nudge_x``, ``nudge_y``. Nudge parameters are used to account for the float and int
          conversions required to display different ranges and values. Conversion are required
          as displays work in integers and not floats

        - **size**: ``width`` and ``height``

        - **color**: ``axes_color``, ``font_color``, ``tick_color``, ``pointer_color``

        - **background color**: ``background_color``

        - **linewidths**: ``axes_stroke`` and ``major_tick_stroke``

        - **range**: ``xrange`` and ``yrange`` This is the range in absolute units.
          For example, when using (20-90), the X axis will start at 20 finishing at 90.
          However, the height of the graph is given by the height parameter. The scale
          is handled internal to provide a 1:1 experience when you update the graph.


    .. figure:: cartesian.gif
       :scale: 100 %
       :figwidth: 50%
       :align: center
       :alt: Diagram of the cartesian widget with the pointer in motion.

       This is a diagram of a cartesian widget with the pointer moving in the
       plot area.

    .. figure:: cartesian_zones.png
       :scale: 100 %
       :figwidth: 50%
       :align: center
       :alt: Diagram of the cartesian widget zones.

       This is a diagram of a cartesian widget showing the different zones.

    .. figure:: cartesian_explanation.png
       :scale: 100 %
       :figwidth: 50%
       :align: center
       :alt: Diagram of the cartesian widget localisation.

       This is a diagram of a cartesian widget showing localisation scheme.

    """

    def __init__(
        self,
        background_color: int = 0x000000,
        xrange: Tuple[int, int] = (0, 100),
        yrange: Tuple[int, int] = (0, 100),
        axes_color: int = 0xFFFFFF,
        axes_stroke: int = 1,
        tick_color: int = 0xFFFFFF,
        major_tick_stroke: int = 1,
        major_tick_length: int = 5,
        tick_label_font: terminalio.FONT = terminalio.FONT,
        font_color: int = 0xFFFFFF,
        pointer_radius: int = 1,
        pointer_color: int = 0xFFFFFF,
        subticks: bool = False,
        nudge_x: int = 0,
        nudge_y: int = 0,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self._verbose = verbose

        self._background_color = background_color

        self._axes_line_color = axes_color
        self._axes_line_thickness = axes_stroke

        self._tick_color = tick_color
        if major_tick_stroke not in range(1, 5):
            print("tick thickness must be 1-4 pixels. Defaulting to 1")
            self._tick_line_thickness = 1
        else:
            self._tick_line_thickness = major_tick_stroke

        if major_tick_length not in range(1, 9):
            print("tick length must be 1-10 pixels. Defaulting to 5")
            self._tick_line_height = 5
        else:
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

        self._plot_bitmap = displayio.Bitmap(self.width, self.height, 5)
        self.clear_plot_lines()
        self._screen_palette = displayio.Palette(6)
        self._screen_palette.make_transparent(0)
        self._screen_palette[1] = self._tick_color
        self._screen_palette[2] = self._axes_line_color
        self._screen_palette[3] = 0x990099
        self._screen_palette[4] = 0xFFFFFF
        self._screen_palette[5] = self._background_color

        self._corner_bitmap = displayio.Bitmap(10, 10, 5)

        bitmaptools.fill_region(
            self._corner_bitmap,
            0,
            0,
            self._axes_line_thickness,
            self._axes_line_thickness,
            2,
        )

        self._corner_tilegrid = displayio.TileGrid(
            self._corner_bitmap,
            pixel_shader=self._screen_palette,
            x=-self._axes_line_thickness,
            y=self.height,
        )

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
            self._plot_bitmap,
            pixel_shader=self._screen_palette,
            x=0,
            y=0,
        )

        self._nudge_x = nudge_x
        self._nudge_y = nudge_y

        self._draw_axes()
        self._draw_ticks()

        self.append(self._axesx_tilegrid)
        self.append(self._axesy_tilegrid)
        self.append(self._screen_tilegrid)
        self.append(self._corner_tilegrid)

        self._pointer: Optional[vectorio.Circle] = None
        self._circle_palette: Optional[displayio.Palette] = None
        self.plot_line_point: List[Tuple[int, int]] = []

    @staticmethod
    def _get_font_height(font: terminalio.FONT, scale: int) -> Tuple[int, int]:
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

    def _draw_axes(self) -> None:
        bitmaptools.fill_region(
            self._axesx_bitmap,
            0,
            0,
            self.width,
            self._axes_line_thickness,
            2,
        )

        bitmaptools.fill_region(
            self._axesy_bitmap,
            self._axesy_width - self._axes_line_thickness,
            0,
            self._axesy_width,
            self.height,
            2,
        )

    def _draw_ticks(self) -> None:
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

                bitmaptools.fill_region(
                    self._axesx_bitmap,
                    text_dist,
                    self._axes_line_thickness,
                    text_dist + self._tick_line_thickness,
                    self._axes_line_thickness + self._tick_line_height,
                    1,
                )

            if self._subticks:
                if i in subticks:
                    # calc subtick_line_height; force min lineheigt to 1.
                    subtick_line_height = max(1, self._tick_line_height // 2)

                    bitmaptools.fill_region(
                        self._axesx_bitmap,
                        text_dist,
                        self._axes_line_thickness,
                        text_dist + 1,
                        self._axes_line_thickness + subtick_line_height,
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

                bitmaptools.fill_region(
                    self._axesy_bitmap,
                    self._axesy_width
                    - self._axes_line_thickness
                    - self._tick_line_height
                    - 1,
                    text_dist,
                    self._axesy_width - self._axes_line_thickness - 1,
                    text_dist + self._tick_line_thickness,
                    1,
                )

            if self._subticks:
                if i in subticks:
                    bitmaptools.fill_region(
                        self._axesy_bitmap,
                        self._axesy_width
                        - self._axes_line_thickness
                        - self._tick_line_height // 2
                        - 1,
                        text_dist,
                        self._axesy_width - self._axes_line_thickness - 1,
                        text_dist + 1,
                        1,
                    )

    def _draw_pointers(self, x: int, y: int) -> None:
        self._circle_palette = displayio.Palette(1)

        self._circle_palette[0] = self._pointer_color
        self._pointer = vectorio.Circle(
            radius=self._pointer_radius, x=x, y=y, pixel_shader=self._circle_palette
        )

        self.append(self._pointer)

    def _calc_local_xy(self, x: int, y: int) -> Tuple[int, int]:
        local_x = (
            int((x - self._xrange[0]) * self._factorx * self._valuex) + self._nudge_x
        )
        # details on `+ (self.height - 1)` :
        # the bitmap is set to self.width & self.height
        # but we are only allowed to draw to pixels 0..height-1 and 0..width-1
        local_y = (
            int((self._yrange[0] - y) * self._factory * self._valuey)
            + (self.height - 1)
            + self._nudge_y
        )
        return (local_x, local_y)

    def _check_local_x_in_range(self, local_x: int) -> bool:
        return 0 <= local_x < self.width

    def _check_local_y_in_range(self, local_y: int) -> bool:
        return 0 <= local_y < self.height

    def _check_local_xy_in_range(self, local_x: int, local_y: int) -> bool:
        return self._check_local_x_in_range(local_x) and self._check_local_y_in_range(
            local_y
        )

    def _check_x_in_range(self, x: int) -> bool:
        return self._xrange[0] <= x <= self._xrange[1]

    def _check_y_in_range(self, y: int) -> bool:
        return self._yrange[0] <= y <= self._yrange[1]

    def _check_xy_in_range(self, x: int, y: int) -> bool:
        return self._check_x_in_range(x) and self._check_y_in_range(y)

    def _add_point(self, x: int, y: int) -> None:
        """_add_point function
        helper function to add a point to the graph in the plane
        :param int x: ``x`` coordinate in the local plane
        :param int y: ``y`` coordinate in the local plane
        :return: None
        rtype: None
        """
        local_x, local_y = self._calc_local_xy(x, y)
        if self._verbose:
            print("")
            print(
                "xy:      ({: >4}, {: >4})  "
                "_xrange: ({: >4}, {: >4})  "
                "_yrange: ({: >4}, {: >4})  "
                "".format(
                    x,
                    y,
                    self._xrange[0],
                    self._xrange[1],
                    self._yrange[0],
                    self._yrange[1],
                )
            )
            print(
                "local_*: ({: >4}, {: >4})  "
                " width:  ({: >4}, {: >4})  "
                " height: ({: >4}, {: >4})  "
                "".format(
                    local_x,
                    local_y,
                    0,
                    self.width,
                    0,
                    self.height,
                )
            )
        if self._check_xy_in_range(x, y):
            if self._check_local_xy_in_range(local_x, local_y):
                if self.plot_line_point is None:
                    self.plot_line_point = []
                self.plot_line_point.append((local_x, local_y))
            else:
                # for better error messages we check in detail what failed...
                # this should never happen:
                # we already checked the range of the input values.
                # but in case our calculation is wrong we handle this case to..
                if not self._check_local_x_in_range(local_x):
                    raise ValueError(
                        "local_x out of range: "
                        "local_x:{: >4}; _xrange({: >4}, {: >4})"
                        "".format(
                            local_x,
                            0,
                            self.width,
                        )
                    )
                if not self._check_local_y_in_range(local_y):
                    raise ValueError(
                        "local_y out of range: "
                        "local_y:{: >4}; _yrange({: >4}, {: >4})"
                        "".format(
                            local_y,
                            0,
                            self.height,
                        )
                    )
        else:
            # for better error messages we check in detail what failed...
            if not self._check_x_in_range(x):
                raise ValueError(
                    "x out of range:    "
                    "x:{: >4}; xrange({: >4}, {: >4})"
                    "".format(
                        x,
                        self._xrange[0],
                        self._xrange[1],
                    )
                )
            if not self._check_y_in_range(y):
                raise ValueError(
                    "y out of range:    "
                    "y:{: >4}; yrange({: >4}, {: >4})"
                    "".format(
                        y,
                        self._yrange[0],
                        self._yrange[1],
                    )
                )

    def update_pointer(self, x: int, y: int) -> None:
        """updater_pointer function
        helper function to update pointer in the plane
        :param int x: ``x`` coordinate in the local plane
        :param int y: ``y`` coordinate in the local plane
        :return: None
        rtype: None
        """

        self._add_point(x, y)
        if not self._pointer:
            self._draw_pointers(
                self.plot_line_point[-1][0],
                self.plot_line_point[-1][1],
            )
        else:
            self._pointer.x = self.plot_line_point[-1][0]
            self._pointer.y = self.plot_line_point[-1][1]

    def add_plot_line(self, x: int, y: int) -> None:
        """add_plot_line function.

        add line to the plane.
        multiple calls create a line-plot graph.

        :param int x: ``x`` coordinate in the local plane
        :param int y: ``y`` coordinate in the local plane
        :return: None

        rtype: None
        """

        self._add_point(x, y)
        if len(self.plot_line_point) > 1:
            bitmaptools.draw_line(
                self._plot_bitmap,
                self.plot_line_point[-2][0],
                self.plot_line_point[-2][1],
                self.plot_line_point[-1][0],
                self.plot_line_point[-1][1],
                1,
            )

    def clear_plot_lines(self, palette_index: int = 5) -> None:
        """clear_plot_lines function.

        clear all added lines
        (clear line-plot graph)

        :param int palette_index: color palett index. Defaults to 5
        :return: None

        rtype: None
        """
        self.plot_line_point = []
        self._plot_bitmap.fill(palette_index)
