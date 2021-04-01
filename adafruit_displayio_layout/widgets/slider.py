# SPDX-FileCopyrightText: 2021 Jose David
#
# SPDX-License-Identifier: MIT
"""

`slider`
================================================================================
A slider widget with a rectangular shape.

* Author(s): Jose David M.

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

################################
# A slider widget for CircuitPython, using displayio and adafruit_display_shapes
#
# Features:
#  - slider to represent non discrete values
#
# Future options to consider:
# ---------------------------
# different orientations (horizontal, vertical, flipped)
#

from adafruit_display_shapes.roundrect import RoundRect
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.control import Control
from adafruit_displayio_layout.widgets.easing import quadratic_easeinout as easing


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class Slider(Widget, Control):

    """

    TBD

    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-locals
    # pylint: disable=too-many-branches, too-many-statements
    def __init__(
        self,
        x=0,
        y=0,
        width=None,  # recommend to default to
        height=40,
        touch_padding=0,
        horizontal=True,  # horizontal orientation
        anchor_point=None,
        anchored_position=None,
        fill_color=(66, 44, 66),
        outline_color=(30, 30, 30),
        background_color=(255, 255, 255),
        background_outline_color=None,  # default to background_color_off
        switch_stroke=2,
        text_stroke=None,  # default to switch_stroke
        value=False,  # initial value
        **kwargs,
    ):

        Widget.__init__(
            self, x=x, y=y, height=height, width=width, **kwargs, max_size=4
        )
        Control.__init__(self)

        self._horizontal = horizontal

        self._knob_width = 20
        self._knob_height = 40

        self._knob_x = self._knob_width
        self._knob_y = self._knob_height

        self._slider_height = 8

        self._height = self.height

        if self._width is None:
            self._width = 50
        else:
            self._width = self.width

        if background_outline_color is None:
            background_outline_color = background_color

        self._fill_color = fill_color
        self._outline_color = outline_color
        self._background_color = background_color
        self._background_outline_color = background_outline_color

        self._switch_stroke = switch_stroke

        if text_stroke is None:
            text_stroke = switch_stroke  # width of lines for the (0/1) text shapes
        self._text_stroke = text_stroke

        self._touch_padding = touch_padding

        self._value = value

        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        self._create_switch()

    def _create_switch(self):
        # The main function that creates the switch display elements
        self._x_motion = self._width
        self._y_motion = 0

        self._frame = RoundRect(
            x=0,
            y=0,
            width=self.width,
            height=self.height,
            r=4,
            fill=0x990099,
            outline=self._outline_color,
            stroke=self._switch_stroke,
        )

        self._switch_handle = RoundRect(
            x=0,
            y=0,
            width=self._knob_width,
            height=self._knob_height,
            r=4,
            fill=self._fill_color,
            outline=self._outline_color,
            stroke=self._switch_stroke,
        )

        self._switch_roundrect = RoundRect(
            x=2,
            y=self.height // 2 - self._slider_height // 2,
            r=2,
            width=self._width - 4,
            height=self._slider_height,
            fill=self._background_color,
            outline=self._background_outline_color,
            stroke=self._switch_stroke,
        )

        self._bounding_box = [
            0,
            0,
            self.width,
            self._knob_height,
        ]

        self.touch_boundary = [
            self._bounding_box[0] - self._touch_padding,
            self._bounding_box[1] - self._touch_padding,
            self._bounding_box[2] + 2 * self._touch_padding,
            self._bounding_box[3] + 2 * self._touch_padding,
        ]

        self._switch_initial_x = self._switch_handle.x
        self._switch_initial_y = self._switch_handle.y

        for _ in range(len(self)):
            self.pop()

        self.append(self._frame)
        self.append(self._switch_roundrect)
        self.append(self._switch_handle)

        self._update_position()

    def _get_offset_position(self, position):

        x_offset = int(self._x_motion * position // 2)
        y_offset = int(self._y_motion * position)

        return x_offset, y_offset

    def _draw_position(self, position):
        # apply the "easing" function to the requested position to adjust motion
        position = easing(position)

        # Get the position offset from the motion function
        x_offset, y_offset = self._get_offset_position(position)

        # Update the switch and text x- and y-positions
        self._switch_handle.x = self._switch_initial_x + x_offset
        self._switch_handle.y = self._switch_initial_y + y_offset

    def selected(self, touch_point):

        touch_x = touch_point[0] - self.x
        touch_y = touch_point[1] - self.y

        self._switch_handle.x = touch_x

        super().selected((touch_x, touch_y, 0))
        return self._switch_handle.x

    def contains(self, touch_point):  # overrides, then calls Control.contains(x,y)
        """Checks if the Widget was touched.  Returns True if the touch_point
        is within the Control's touch_boundary.

        :param touch_point: x,y location of the screen, in absolute display coordinates.
        :return: Boolean

        """
        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        return super().contains((touch_x, touch_y, 0))

    @property
    def value(self):
        """The current switch value (Boolean).

        :return: Boolean
        """
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            fake_touch_point = [0, 0, 0]  # send an arbitrary touch_point
            self.selected(fake_touch_point)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, new_width):
        if self._width is None:
            self._width = 50
        else:
            self._width = new_width
        self._create_switch()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, new_height):
        self._height = new_height
        self._width = new_height // 2
        self._create_switch()

    def resize(self, new_width, new_height):
        """Resize the switch to a new requested width and height.

        :param int new_width: requested maximum width
        :param int new_height: requested maximum height
        :return: None

        """

        # Swap dimensions when orientation is vertical: "horizontal=False"
        if not self._horizontal:
            new_width, new_height = new_height, new_width

        # calculate the preferred target width based on new_height and 2:1 aspect ratio
        preferred_width = new_height * 2

        if preferred_width <= new_width:  # the new_height is the constraint
            self._height = new_height
            self._width = preferred_width
        else:  # the new_width is the constraint
            self._height = new_width // 2  # keep 2:1 aspect ratio
            self._width = new_width

        self._width = self._height // 2

        self._create_switch()
