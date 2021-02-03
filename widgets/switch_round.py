# The MIT License (MIT)
#
# Copyright (c) 2021 Kevin Matocha (kmatch98)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
################################
# A round switch widget for CircuitPython, using displayio and adafruit_display_shapes
#
# Features:
#  - Color grading as the switch animates between the off and on states
#  - Option to display 0 or 1 to confirm the switch state (display_button_text=True)
#  - Provides setting for animation_time (approximate), and adapts redraw rate based on real time.
#
# Future options to consider:
# ---------------------------
# different orientations (horizontal, vertical, flipped)
#

import time
import terminalio
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.rect import Rect
from widget import Widget
from control import Control
from widget_label import WidgetLabel


class SwitchRound(Widget, Control):
    """A horizontal sliding switch widget.  The origin is set using ``x`` and ``y``.

    :param int x: pixel position
    :param int y: pixel position
    :param int width: width of the switch in pixels, set to ``None`` to auto-size
     relative to the height
    :param int height: height of the switch in pixels
    :param str name: name of the switch
    :param float anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor
     point relative to the switch bounding box
    :param int anchored_position: (x,y) pixel value for the location
     of the anchor_point
    :param fill_color_off: switch off-state fill color (RGB tuple
     or 24-bit hex value)
    :param fill_color_on: switch on-state fill color (RGB tuple or
     24-bit hex value)
    :param outline_color_off: switch off-state outline color (RGB
     tuple or 24-bit hex value)
    :param outline_color_on: switch on-state outline color (RGB tuple
     or 24-bit hex value)
    :param background_color_off: background off-state color (RGB tuple
     or 24-bit hex value)
    :param background_color_on: background on-state color (RGB tuple
     or 24-bit hex value)
    :param background_outline_color_off: background outline off-state
     color (RGB tuple or 24-bit hex value)
    :param background_outline_color_on: background outline on-state
     color (RGB tuple or 24-bit hex value)
    :param int switch_stroke: outline stroke width for the switch, in pixels
    :param int text_stroke: outline stroke width for the 0/1 text, in pixels
    :param Boolean display_button_text: Set True to display the 0/1 text
     on the sliding switch
    :param float animation_time: time for the switching animation, in seconds
     a value of 0.2 is a good starting point"""

    # This Switch has multiple class inheritances.
    # It is a subclass of Group->Widget and a sublcass of Control.

    def __init__(
        self,
        value=False,
        touch_padding=0,
        anchor_point=None,
        anchored_position=None,
        fill_color_off=(66, 44, 66),
        fill_color_on=(0, 100, 0),
        outline_color_off=(30, 30, 30),
        outline_color_on=(0, 60, 0),
        background_color_off=(255, 255, 255),
        background_color_on=(0, 60, 0),
        background_outline_color_off=None,  # default to background_color_off
        background_outline_color_on=None,  # default to background_color_on
        switch_stroke=2,
        text_stroke=None,  # default to switch_stroke
        display_button_text=True,
        animation_time=0.2,  # animation duration (in seconds)
        horizontal=True,  # horizontal orientation
        flip=False,  # flip the direction of the switch movement
        label_anchor_point=(1, 0.5),  # default label position
        label_anchor_on_widget=(-0.05, 0.5),  # default label position on widget
        **kwargs,
    ):

        # initialize the Widget superclass (x, y, scale)
        super().__init__(**kwargs, max_size=4)
        # Define how many graphical elements will be in this group
        # using "max_size=XX"
        #
        # Group elements for SwitchRoundHorizontal:
        #  1. switch_roundrect: The switch background
        #  2. switch_circle: The switch button
        #  3. Optional - widget label
        #  4. Optional - text_0 or text_1: The 0/1 text on the switch button

        # initialize the Control superclass
        super(Control, self).__init__()

        self._radius = self.height // 2
        switch_x = self._radius
        switch_y = self._radius

        if self._width is None:
            self._width = 4 * self._radius
        else:
            self._width = self._width

        if background_outline_color_off is None:
            background_outline_color_off = background_color_off
        if background_outline_color_on is None:
            background_outline_color_on = background_color_on

        self._fill_color_off = fill_color_off
        self._fill_color_on = fill_color_on
        self._outline_color_off = outline_color_off
        self._outline_color_on = outline_color_on
        self._background_color_off = background_color_off
        self._background_color_on = background_color_on
        self._background_outline_color_off = background_outline_color_off
        self._background_outline_color_on = background_outline_color_on

        self._switch_stroke = switch_stroke

        if text_stroke is None:
            text_stroke = switch_stroke  # width of text lines
        self._text_stroke = text_stroke

        self._display_button_text = (
            display_button_text  # state variable whether text (0/1) is displayed
        )

        self._touch_padding = touch_padding

        self._animation_time = animation_time

        self._value = value

        self._text_0_on = not value  # controls which text value is displayed (0 or 1)

        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        self._label_anchor_point = label_anchor_point
        self._label_anchor_on_widget = label_anchor_on_widget

        # Define the motion "keyframes" that define the switch movement
        if horizontal:  # horizontal switch orientation
            self._x_motion = self._width - 2 * self._radius - 1
            self._y_motion = 0

        else:  # vertical orientation
            self._x_motion = 0
            self._y_motion = self._width - 2 * self._radius - 1

        self._angle_motion = 0

        if flip:
            self._x_motion = -1 * self._x_motion
            self._y_motion = -1 * self._y_motion
            self._angle_motion = -1 * self._angle_motion

        # Initialize the display elements - These should depend upon the
        # orientation (`horizontal` and `flip`)
        #
        # Initialize the Circle

        circle_x0 = switch_x
        circle_y0 = switch_y
        if flip:
            circle_x0 = circle_x0 - self._x_motion
            circle_y0 = circle_y0 - self._y_motion

        self._switch_circle = Circle(
            x0=circle_x0,
            y0=circle_y0,
            r=self._radius,
            fill=self._fill_color_off,
            outline=self._outline_color_off,
            stroke=self._switch_stroke,
        )

        # Initialize the RoundRect for the background
        if horizontal:  # Horizontal orientation
            self._switch_roundrect = RoundRect(
                x=switch_x - self._radius,
                y=switch_y - self._radius,
                r=self._radius,
                width=self._width,
                height=2 * self._radius + 1,
                fill=self._background_color_off,
                outline=self._background_outline_color_off,
                stroke=self._switch_stroke,
            )
        else:  # Vertical orientation
            self._switch_roundrect = RoundRect(
                x=switch_x - self._radius,
                y=switch_y - self._radius,
                r=self._radius,
                width=2 * self._radius + 1,
                height=self._width,
                fill=self._background_color_off,
                outline=self._background_outline_color_off,
                stroke=self._switch_stroke,
            )

        # The "0" text circle
        self._text_0 = Circle(
            x0=circle_x0,
            y0=circle_y0,
            r=self._radius // 2,
            fill=self._fill_color_off,
            outline=self._outline_color_off,
            stroke=self._text_stroke,
        )

        # The "1" text rectangle
        # Needs to adapt to flip and horizontal
        text1_x_offset = (-1 * self._switch_stroke) + 1
        text1_y_offset = -self._radius // 2

        # if flip:
        #     text1_x_offset = -1 * text1_x_offset
        #     text1_y_offset = -1 * text1_y_offset

        self._text_1 = Rect(
            x=circle_x0 + text1_x_offset,
            y=circle_y0 + text1_y_offset,
            height=self._radius,
            width=self._text_stroke,
            fill=self._fill_color_off,
            outline=self._outline_color_off,
            stroke=self._text_stroke,
        )

        # bounding_box defines the "local" x and y.
        # Must be offset by self.x and self.y to get the raw display coordinates
        #

        if horizontal:  # Horizontal orientation
            self._bounding_box = [
                0,
                0,
                self._width,
                2 * self._radius + 1,
            ]
        else:  # Vertical orientation
            self._bounding_box = [
                0,
                0,
                2 * self._radius + 1,
                self._width,
            ]

        self.touch_boundary = [
            self._bounding_box[0] - self._touch_padding,
            self._bounding_box[1] - self._touch_padding,
            self._bounding_box[2] + 2 * self._touch_padding,
            self._bounding_box[3] + 2 * self._touch_padding,
        ]

        # Store initial positions of all moving elements
        self._switch_initial_x = self._switch_circle.x
        self._switch_initial_y = self._switch_circle.y

        self._text_0_initial_x = self._text_0.x
        self._text_0_initial_y = self._text_0.y
        self._text_1_initial_x = self._text_1.x
        self._text_1_initial_y = self._text_1.y

        # Set the initial switch position based on the starting value
        if value:
            self._draw_position(1)
        else:
            self._draw_position(0)

        # Add the display elements to the self group
        self.append(self._switch_roundrect)
        self.append(self._switch_circle)

        # Create the widget label
        self.widget_label = None
        if self.name != "":
            font = terminalio.FONT
            self.widget_label = WidgetLabel(
                font,
                self,
                anchor_point=self._label_anchor_point,
                anchor_point_on_widget=self._label_anchor_on_widget,
            )

        # If display_button_text is True, append the correct text element (0 or 1)
        if display_button_text:
            if self._text_0_on:
                self.append(self._text_0)
            else:
                self.append(self._text_1)

        # update the position, if required
        self._update_position()

    def _get_offset_position(self, position):
        # Function to calculate the offset position (x, y, angle) of the moving
        # elements of an animated widget
        # input parameter `position` is a value from 0.0 to 1.0 indicating start
        # and end position
        #
        # Designed to be flexible depending upon the widget's response
        #
        # values should be set in the __init__ function:
        #     self._x_motion: x-direction movement in pixels
        #     self._y_motion: y-direction movement in pixels
        #     self._angle_motion: angle movement
        #
        # A linear movement function (but can be modified for other motion acceleration)
        if position < 0:
            position = 0
        if position > 1:
            position = 1

        # if multiple elements are present, they could each have their own movement functions.
        x_offset = int(self._x_motion * position)
        y_offset = int(self._y_motion * position)
        angle_offset = self._angle_motion * position

        return x_offset, y_offset, angle_offset

    def _draw_position(self, position):
        # Draw the position of the slider.
        # The position parameter is a float between 0 and 1 (0= off, 1= on).

        # Get the position offset from the motion function
        x_offset, y_offset, angle_offset = self._get_offset_position(position)

        # Update the switch and text x- and y-positions
        self._switch_circle.x = self._switch_initial_x + x_offset
        self._switch_circle.y = self._switch_initial_y + y_offset
        self._text_0.x = self._text_0_initial_x + x_offset
        self._text_0.y = self._text_0_initial_y + y_offset
        self._text_1.x = self._text_1_initial_x + x_offset
        self._text_1.y = self._text_1_initial_y + y_offset

        # Set the color to the correct fade
        self._switch_circle.fill = _color_fade(
            self._fill_color_off, self._fill_color_on, position
        )
        self._switch_circle.outline = _color_fade(
            self._outline_color_off, self._outline_color_on, position
        )

        self._switch_roundrect.fill = _color_fade(
            self._background_color_off, self._background_color_on, position
        )
        self._switch_roundrect.outline = _color_fade(
            self._background_outline_color_off,
            self._background_outline_color_on,
            position,
        )

        self._text_0.fill = self._switch_circle.fill
        self._text_1.fill = self._switch_circle.fill
        self._text_0.outline = self._switch_circle.outline
        self._text_1.outline = self._switch_circle.outline

        if self._display_button_text and position > 0.5 and self._text_0_on:
            self.pop()
            self.append(self._text_1)
            self._text_0_on = False

        elif self._display_button_text and position < 0.5 and not self._text_0_on:
            self.pop()
            self.append(self._text_0)
            self._text_0_on = True

    def selected(self, touch_point):
        # requires passing display to allow auto_refresh off when redrawing
        # touch_point is adjusted for group's x,y position before sending to super()

        start_time = time.monotonic()

        while True:
            if self._value:
                position = (
                    1 - (time.monotonic() - start_time) / self._animation_time
                )  # fraction from 0 to 1
            else:
                position = (
                    time.monotonic() - start_time
                ) / self._animation_time  # fraction from 0 to 1

            self._draw_position(position)  # update the switch position

            if (
                position >= 1
            ) and not self._value:  # ensures that the final position is drawn
                self._value = True
                break
            if (
                position <= 0
            ) and self._value:  # ensures that the final position is drawn
                self._value = False
                break

            touch_x = (
                touch_point[0] - self.x
            )  # adjust touch position for the local position
            touch_y = touch_point[1] - self.y

            super().selected((touch_x, touch_y, 0))

    def contains(self, touch_point):  # overrides, then calls Control.contains(x,y)
        """Returns True if the touch_point is within the widget's touch_boundary."""
        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        return super().contains((touch_x, touch_y, 0))

    @property
    def value(self):
        """The current switch value (Boolean)."""
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            fake_touch_point = [0, 0, 0]  # send an arbitrary touch_point
            self.selected(fake_touch_point)


######  color support functions  ######


def _color_to_tuple(value):
    """Converts a color from a 24-bit integer to a tuple.
    :param value: RGB LED desired value - can be a RGB tuple or a 24-bit integer.
    """
    if isinstance(value, tuple):
        return value
    if isinstance(value, int):
        if value >> 24:
            raise ValueError("Only bits 0->23 valid for integer input")
        r = value >> 16
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return [r, g, b]
    else:
        raise ValueError("Color must be a tuple or 24-bit integer value.")


def _color_fade(start_color, end_color, fraction):
    """Linear extrapolation of a color between two RGB colors (tuple or 24-bit integer).
    : param start_color: starting color
    : param end_color: ending color
    : param fraction: Floating point number  ranging from 0 to 1 indicating what
    fraction of interpolation between start_color and end_color.
    """

    start_color = _color_to_tuple(start_color)
    end_color = _color_to_tuple(end_color)
    if fraction >= 1:
        return end_color
    if fraction <= 0:
        return start_color

    faded_color = [0, 0, 0]
    for i in range(3):
        faded_color[i] = start_color[i] - int(
            (start_color[i] - end_color[i]) * fraction
        )
    return faded_color
