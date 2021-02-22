# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
"""

`switch_round`
================================================================================
CircuitPython GUI Widget Class for visual elements

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

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
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.rect import Rect
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.control import Control
from adafruit_displayio_layout.widgets.easing import BackEaseInOut as easing

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class SwitchRound(Widget, Control):
    """A horizontal sliding switch widget.  The origin is set using ``x`` and ``y``.

        :param int x: pixel position
        :param int y: pixel position
        :param int width: width of the switch in pixels, set to ``None`` to auto-size
         relative to the height
        :param int height: height of the switch in pixels
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
         a value of 0.2 is a good starting point

    Details of the `SwitchRound` widget

        The `SwitchRound` widget is a graphical element that responds to touch elements
        to provide sliding switch on/off behavior.  Whenever touched, the switch toggles
        to its alternate value. The following sections describe the construction of the
        `SwitchRound` widget, in the hopes that it will serve as an example of the key
        properties and responses for widgets.

        The `SwitchRound` widget inherits from two classes, it is a subclass of Group->Widget
        and a sublcass of Control.  The `Widget` class helps define the positioning and
        sizing of the switch, while the `Control` class defines the touch-response behavior.

    Group structure: Display elements that make up SwitchRound

    Coordinate systems:
    See the `Widget` class definition

    Construction sequence:
    - Build stationary items
    - Build moving items
    - Store initial position
    - Define "keyframes" and/or translation vector
    - Define draw position function (0.0 to 1.0 and beyond)
    - Define motion "easing" function

    Translation, keyframes, motion functions and easing, and animation time handling.
    Resizing with constraints
    Orientation - peculiarity of width and height
    Bounding box - see Widget class definition
    Touch boundary, touch-padding - see Widget class definition

    Class structure - review if inheritance is captured in the documentation

    Highlight options:
    - orientation
    - touch-padding
    - text on switch
    - Coloring

    """

    def __init__(
        self,
        x=0,
        y=0,
        height=40,
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
        **kwargs,
    ):

        # initialize the Widget superclass (x, y, scale)
        super().__init__(x=x, y=y, height=height, **kwargs, max_size=4)
        # Define how many graphical elements will be in this group
        # using "max_size=XX"
        #
        # Group elements for SwitchRound:
        #  0. switch_roundrect: The switch background
        #  1. switch_circle: The switch button
        #  2. Optional: text_0: The "0" circle on the switch button
        #  3. Optional: text_1: The "1" rectangle  on the switch button

        # initialize the Control superclass
        super(Control, self).__init__()

        self._horizontal = horizontal
        self._flip = flip

        # height and width internal variables are treated before considering rotation
        self._height = self.height
        self._radius = self.height // 2

        # If width is not provided, then use the preferred aspect ratio
        if self._width is None:
            self._width = 4 * self._radius
        else:
            self._width = self.width

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
            text_stroke = switch_stroke  # width of lines for the (0/1) text shapes
        self._text_stroke = text_stroke

        self._display_button_text = display_button_text
        # state variable whether (0/1) text shapes is displayed

        self._touch_padding = touch_padding

        self._animation_time = animation_time

        self._value = value

        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        self._create_switch()

    def _create_switch(self):
        # The main function that creates the switch display elements

        switch_x = self._radius
        switch_y = self._radius

        # Define the motion "keyframes" that define the switch movement
        if self._horizontal:  # horizontal switch orientation
            self._x_motion = self._width - 2 * self._radius - 1
            self._y_motion = 0

        else:  # vertical orientation
            self._x_motion = 0
            self._y_motion = self._width - 2 * self._radius - 1

        self._angle_motion = 0

        if self._flip:
            self._x_motion = -1 * self._x_motion
            self._y_motion = -1 * self._y_motion
            self._angle_motion = -1 * self._angle_motion

        # Initialize the display elements - These should depend upon the
        # orientation (`horizontal` and `flip`)
        #
        # Initialize the Circle

        circle_x0 = switch_x
        circle_y0 = switch_y

        if self._flip:
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
        if self._horizontal:  # Horizontal orientation
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

        # The "0" text circle shape
        self._text_0 = Circle(
            x0=circle_x0,
            y0=circle_y0,
            r=self._radius // 2,
            fill=self._fill_color_off,
            outline=self._outline_color_off,
            stroke=self._text_stroke,
        )

        # The "1" text rectangle shape
        text1_x_offset = (-1 * self._switch_stroke) + 1
        text1_y_offset = -self._radius // 2

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
        if self._horizontal:  # Horizontal orientation
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

        # Store initial positions of moving elements to be used in _draw_function
        self._switch_initial_x = self._switch_circle.x
        self._switch_initial_y = self._switch_circle.y

        self._text_0_initial_x = self._text_0.x
        self._text_0_initial_y = self._text_0.y
        self._text_1_initial_x = self._text_1.x
        self._text_1_initial_y = self._text_1.y

        # Set the initial switch position based on the starting value
        if self._value:
            self._draw_position(1)
        else:
            self._draw_position(0)

        # pop any items off the current self group, in case this is updating
        # an existing switch
        for _ in range(len(self)):
            self.pop()

        # Add the display elements to the self group
        self.append(self._switch_roundrect)
        self.append(self._switch_circle)

        # If display_button_text is True, append the correct text element (0 or 1)
        if self._display_button_text:
            self.append(self._text_0)
            self.append(self._text_1)
            if self._value:
                self._text_0.hidden = True
                self._text_1.hidden = False
            else:
                self._text_0.hidden = False
                self._text_1.hidden = True

        # update the anchor position, if required
        # this calls the parent Widget class to update the anchored_position
        # due to any changes that might have occurred in the bounding_box
        self._update_position()

    def _get_offset_position(self, position):
        # Function to calculate the offset position (x, y, angle) of the moving
        # elements of an animated widget.  Designed to be flexible depending upon
        # the widget's desired response.
        #
        # The input parameter `position` is a value from 0.0 to 1.0 indicating the
        # start (0.0) and end (1.0) positions.
        #
        # For this linear translation, the following values are set in __init__:
        #     self._x_motion: x-direction movement in pixels
        #     self._y_motion: y-direction movement in pixels
        #     self._angle_motion: angle movement

        # This defines the tranfer function between position and motion.
        # for switch, this is a linear translation function, rotation is actually ignored.
        # Alternate functions (log, power, exponential) could be used
        x_offset = int(self._x_motion * position)
        y_offset = int(self._y_motion * position)
        angle_offset = self._angle_motion * position

        return x_offset, y_offset, angle_offset

    def _draw_position(self, position):
        # Draw the position of the slider.
        # The position parameter is a float between 0 and 1 (0= off, 1= on).

        # apply the "easing" function to the requested position to adjust motion
        position = easing(position)

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

        if self._display_button_text and position >= 0.5:
            self._text_0.hidden = True
            self._text_1.hidden = False

        elif self._display_button_text and position < 0.5:
            self._text_0.hidden = False
            self._text_1.hidden = True

    def _animate_switch(self):
        # The animation function for the switch.
        # 1.  Move the switch
        # 2.  Update the self._value to the opposite of its current value.
        #
        # Depending upon your widget's animation requirements,
        # you can change this function to control the acceleration
        # and motion of your element.
        #
        # Key animation feature:
        #  - Uses the timer to control the speed of the motion.  This ensure
        #      that the movement speed will be the same on different boards.
        #

        start_time = time.monotonic()  # set the starting time for animation

        while True:

            # This determines the direction of movement, depending upon if the
            # switch is going from on->off or off->on
            #
            # Note: This is currently written with a constant speed of movement.
            # Adjust this `position` function if you want a nonlinear
            # acceleration of the motion.  There will be interaction between
            # this function and `_draw_position` and `_get_offset_position`
            # to control the position and the motion speed.
            #
            if self._value:
                position = (
                    1 - (time.monotonic() - start_time) / self._animation_time
                )  # fraction from 0 to 1
            else:
                position = (
                    time.monotonic() - start_time
                ) / self._animation_time  # fraction from 0 to 1

            # Update the moving elements based on the current position

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

    def selected(self, touch_point):
        """Response function when Switch is selected.  When selected, the switch
        position and value is changed with an animation.

        :param touch_point: x,y location of the screen, in absolute display coordinates.
        :return: None

        """

        self._animate_switch()  # show the animation and switch the self._value

        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        # Call the parent's .selected function in case there is any work up there.
        # touch_point is adjusted for group's x,y position before sending to super()
        super().selected((touch_x, touch_y, 0))

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
            self._width = 4 * self._radius
        else:
            self._width = new_width
        self._create_switch()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, new_height):
        self._height = new_height
        self._radius = new_height // 2
        self._create_switch()

    def resize(self, new_width, new_height):
        """Resize the switch to a new requested width and height.

        :param int new_width: requested maximum width
        :param int new_height: requested maximum height
        :return: None

        """
        # Fit the new button size within the requested maximum width/height
        # dimensions, but keeping an aspect ratio of 2:1 (width:height)

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

        self._radius = self._height // 2

        self._create_switch()


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

    raise ValueError("Color must be a tuple or 24-bit integer value.")


def _color_fade(start_color, end_color, fraction):
    """Linear extrapolation of a color between two RGB colors (tuple or 24-bit integer).
    :param start_color: starting color
    :param end_color: ending color
    :param fraction: Floating point number  ranging from 0 to 1 indicating what
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
