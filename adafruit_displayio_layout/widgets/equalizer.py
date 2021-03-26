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
from adafruit_displayio_layout.widgets import rgb

try:
    from adafruit_fancyled.adafruit_fancyled import CRGB
except NameError:
    pass


class Equalizer(Widget):
    """An equalizer widget.  The origin is set using ``x`` and ``y``.

    :param int x: x position of the plane origin
    :param int y: y position of the plane origin

    :param int width: requested width, in pixels.
    :param int height: requested height, in pixels.

    :param int background_color: background color to use defaults to black (0x000000)

    :para int number_bars: number of bar in the equalizer. Defaults to 1.
    :para bool bar_best_fit: Allows selecting the best fit for the bar in the given width
    :param int bar_width: width in pixels of the equalizers bar. Defaults to 10.

    :param int pad_x: pixels number to move the bars to the right

    :param int number_segments: number of segments in each bar
    :param int segments_height: height in pixel of each bar equalizer segment
    :param bool seg_best_fit: When True it will calculate segment height automatically
     Defaults to True.


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

    **Summary: Cartesian Features and input variables**

    The `cartesian` widget has some options for controlling its position, visible appearance,
    and scale through a collection of input variables:

        - **position**: ``x``, ``y``

        - **size**: ``width`` and ``height``

        - **color**: color is controlled internally, to ease the use of the widget

        - **background color**: ``background_color``

        - **range**: range is controlled internally to ease the use of the widget and is set
          to 100. To have other ranges, normalize your values first and the pass them to the
          updater.


    .. figure:: equalizer.gif
       :scale: 100 %
       :figwidth: 50%
       :align: center
       :alt: Picture of the equalizer widget in motion.

       This shows the equalizer capabilities.


    """

    def __init__(
        self,
        background_color: int = 0x000000,
        number_bars: int = 1,
        bar_best_fit: bool = True,
        bar_width: int = 10,
        pad_x: int = 0,
        number_segments: int = 2,
        segments_height: int = 10,
        seg_best_fit: bool = True,
        **kwargs,
    ) -> None:

        # TODO Segment display              [✓]
        # TODO SEGMENT level logic          [✓]
        # TODO Animation function           [✓]
        # TODO Animated Gifs                [✓]
        # TODO SimpleTest example           [✓]
        # TODO Features docs                [✓]
        # TODO PNGs                         [✓]
        # TODO Type Annotations             [✓]
        # TODO API example inclusion        [✓]
        # TODO API RST inclusion            [✓]
        # TODO Black Pylint example         [✓]
        # TODO Black Pylint __init__        [✓]

        super().__init__(**kwargs, max_size=3)

        self._background_color = background_color

        if self.width < 42:
            print("Equalizer minimum width is 40. Defaulting to 40")
            self._width = 40

        self._number_bars = number_bars
        self._bar_width = bar_width
        self._pad_x = pad_x
        self._bar_best_fit = bar_best_fit

        self._number_segments = number_segments
        self._segments_height = segments_height
        self._seg_best_fit = seg_best_fit

        self._screen_bitmap = displayio.Bitmap(self.width, self.height, 5)
        self._screen_bitmap.fill(10)
        self._screen_palette = displayio.Palette(11)
        self._screen_palette[10] = self._background_color

        self._bar_inventory = list()
        self._segment_inventory = list()
        self._hor_bar_setup()

        self._screen_tilegrid = displayio.TileGrid(
            self._screen_bitmap,
            pixel_shader=self._screen_palette,
            x=0,
            y=0,
        )

        self.append(self._screen_tilegrid)

    def _hor_bar_setup(self):
        if self._bar_best_fit:
            self._bar_width = (
                self.width - 2 * (self._number_bars + 1)
            ) // self._number_bars
        else:
            total_width = self._number_bars * self._bar_width + (
                (self._number_bars + 1) * 2
            )

            if total_width > self.width:
                print("Equalizer setup could not be displayed. Adjusting bar widths")
                self._bar_width = (
                    self.width - ((self._number_bars + 1) * 2)
                ) // self._number_bars

        widths_bars = self._number_bars * self._bar_width
        width_free = self.width - widths_bars
        separationx = width_free // (self._number_bars + 1)
        x_local = separationx + self._pad_x

        if self._seg_best_fit:
            self._segments_height = (self.height - 2) // self._number_segments
        else:
            total_height = self._number_segments * self._segments_height + 6
            if total_height > self.height:
                print(
                    "Equalizer setup could not be displayed. Adjusting segments heights"
                )
                self._segments_height = (
                    self.height - ((self._number_segments + 1) * 2)
                ) // self._number_segments

        heights_segs = self._number_segments * self._segments_height
        height_free = self.height - heights_segs
        self._separationy = height_free // (self._number_segments + 1)

        for col in range(self._number_bars):
            self._bar_inventory.append((col, x_local))
            x_local = x_local + separationx + self._bar_width

        y_local = self.height - self._separationy - self._segments_height
        delta = 100 // self._number_segments
        trigger_value = 0

        for row in range(self._number_segments):
            self._segment_inventory.append((row, y_local, trigger_value, 0))
            y_local = y_local - self._separationy - self._segments_height
            trigger_value = trigger_value + delta

        for i, item in enumerate(self._segment_inventory):
            prgb_color = rgb(item[1], 0, 100)
            color_buffer = CRGB(prgb_color[0], prgb_color[1], prgb_color[2])
            self._screen_palette[i] = color_buffer.pack()

    def show_bars(self, values) -> None:
        """
        :parm values: Tuple of values to update the equlizer bars
        """
        for j, element in enumerate(self._segment_inventory):
            for i, _ in enumerate(self._bar_inventory):
                if element[2] < values[i]:

                    rectangle_helper(
                        self._bar_inventory[i][1],
                        self._segment_inventory[j][1],
                        self._segments_height,
                        self._bar_width,
                        self._screen_bitmap,
                        j,
                        self._screen_palette,
                    )
                else:
                    rectangle_helper(
                        self._bar_inventory[i][1],
                        self._segment_inventory[j][1],
                        self._segments_height,
                        self._bar_width,
                        self._screen_bitmap,
                        10,
                        self._screen_palette,
                    )
