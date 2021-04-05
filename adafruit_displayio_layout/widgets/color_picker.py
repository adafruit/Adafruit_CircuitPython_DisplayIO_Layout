# SPDX-FileCopyrightText: 2021 Jose David
#
# SPDX-License-Identifier: MIT
"""

`color_picker`
================================================================================
A colorpicker using a existing bitmap created by the make_wheel utility.

* Author(s): Jose David M.

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

################################
# A color picker for CircuitPython, using displayio
#
# Features:
#  - color picker using a existing Bitmap
#
# Future options to consider:
# ---------------------------
# Better color wheel logic
# Sliders to mix Red, Green and Blue
#

import math
from displayio import TileGrid, OnDiskBitmap, ColorConverter
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.control import Control


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class ColorPicker(Widget, Control):
    """A widget to be used to select colors from a heel.

    :param str filename: name of the bitmap file to be used as a ColorPicker

    :param int x: x position of the color picker origin
    :param int y: y position of the color picker origin

    :param int imagesize: size of the bitmap file. The bitmap colorwheels are squares.


    **Quickstart: Importing and using the Color Picker**

    Here is one way of importing the ``ColorPicker`` class so you can use:

    .. code-block:: python

        from adafruit_displayio_layout.widgets.color_picker import ColorPicker

    Now you can create an Slider at pixel position x=20, y=30 using:

    .. code-block:: python

        my_colorpicker=ColorPicker(x=20, y=30)

    Once you setup your display, you can now add ``my_colorpicker`` to your display using:

    .. code-block:: python

        display.show(my_colorpicker) # add the group to the display

    If you want to have multiple display elements, you can create a group and then
    append the slider and the other elements to the group.  Then, you can add the full
    group to the display as in this example:

    .. code-block:: python

        my_colorpicker= ColorPicker(20, 30)
        my_group = displayio.Group(max_size=10) # make a group that can hold 10 items
        my_group.append(my_colorpicker) # Add my_slider to the group

        #
        # Append other display elements to the group
        #

        display.show(my_group) # add the group to the display


    **Final Notes**

    Depending on the screen results may vary. Resolution of the bitmap will no be as seen in a PC.
    Sensitivity of the screen could also affect the behaviour of the library.


    **The Color Picker Widget**

    .. figure:: color_picker.png
      :scale: 100 %
      :align: center
      :alt: Example of the color picker widget.

      Example of the color picker. representation will vary according to screen used.



    """

    # pylint: disable=too-many-lines, too-many-instance-attributes, too-many-arguments
    # pylint: disable=too-many-locals, too-many-statements

    def __init__(
        self,
        filename: str = None,
        x: int = 0,
        y: int = 0,
        image_size: int = 100,
        **kwargs,
    ):

        Widget.__init__(
            self, x=x, y=y, height=image_size, width=image_size, **kwargs, max_size=4
        )
        Control.__init__(self)

        self._file = open(filename, "rb")
        image = OnDiskBitmap(self._file)
        tile_grid = TileGrid(image, pixel_shader=ColorConverter())

        self._image_size = image_size

        self.append(tile_grid)

        self.touch_boundary = (
            0,
            0,
            image.width,
            image.height,
        )

    def contains(self, touch_point):  # overrides, then calls Control.contains(x,y)

        """Checks if the ColorPicker was touched.  Returns True if the touch_point is
        within the ColorPicker's touch_boundary.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :type touch_point: Tuple[x,y]
        :return: Boolean
        """

        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        return super().contains((touch_x, touch_y, 0))

    def when_selected(self, touch_point, screen_height):
        """Response function when ColorPicker is selected.  When selected, the ColorPicker
        will give the color corresponding with the position

        :param touch_point: x,y location of the screen, in absolute display coordinates.
        :param int screen_height: screen height
        :return: Color

        """

        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = screen_height - touch_point[1] - self.y

        # Call the parent's .selected function in case there is any work up there.
        # touch_point is adjusted for group's x,y position before sending to super()
        super().selected((touch_x, touch_y, 0))
        return self._color_from_position(touch_x, touch_y, self._image_size)

    def _color_from_position(self, x, y, image_size):
        img_half = image_size // 2
        dist = abs(math.sqrt((x - img_half) ** 2 + (y - img_half) ** 2))
        if x - img_half == 0:
            angle = -90
            if y > img_half:
                angle = 90
        else:
            angle = math.atan2((y - img_half), (x - img_half)) * 180 / math.pi

        angle = (angle + 30) % 360

        shade = 1 * dist / img_half
        idx = angle / 60
        base = int(round(idx))
        adj = (6 + base + (-1 if base > idx else 1)) % 6
        ratio = max(idx, base) - min(idx, base)
        color = self._make_color(base, adj, ratio, shade)

        return color

    @staticmethod
    def _make_color(base, adj, ratio, shade):
        """
        Go through each bit of the colors adjusting blue with blue, red with red,
        green with green, etc.
        """
        color_wheel = [
            [0xFF, 0x00, 0xFF],
            [0xFF, 0x00, 0x00],
            [0xFF, 0xFF, 0x00],
            [0x00, 0xFF, 0x00],
            [0x00, 0xFF, 0xFF],
            [0x00, 0x00, 0xFF],
            [0xFF, 0x00, 0xFF],
        ]

        output = 0x0
        bit = 0

        for pos in range(3):
            base_chan = color_wheel[base][pos]
            adj_chan = color_wheel[adj][pos]
            new_chan = int(round(base_chan * (1 - ratio) + adj_chan * ratio))

            # now alter the channel by the shade
            if shade < 1:
                new_chan = new_chan * shade
            elif shade > 1:
                shade_ratio = shade - 1
                new_chan = (0xFF * shade_ratio) + (new_chan * (1 - shade_ratio))

            output = output + (int(new_chan) << bit)
            bit = bit + 8
        return output
