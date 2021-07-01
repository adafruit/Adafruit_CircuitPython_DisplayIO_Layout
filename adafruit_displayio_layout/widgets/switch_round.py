# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
"""

`switch_round`
================================================================================
A sliding switch widget with a round shape.

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

# modify the "easing" function that is imported to change the switch animation behaviour
from adafruit_displayio_layout.widgets.easing import back_easeinout as easing


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class SwitchRound(Widget, Control):

    """
    .. note:: Jump directly to:

        - :ref:`SwitchRound: Input parameters <parameters>`
        - :ref:`SwitchRound: Methods <methods>`
        - :ref:`SwitchRound: Description of implementation <links>`

    .. _parameters:

    :param int x: pixel position, defaults to 0
    :param int y: pixel position, defaults to 0
    :param int width: width of the switch in pixels, if set to None (**recommended**)
     the width will auto-size relative to the height, defaults to None
    :param int height: height of the switch in pixels, defaults to 40 pixels
    :param int touch_padding: the width of an additional border surrounding the switch
     that extends the touch response boundary, defaults to 0
    :param Boolean horizontal: To set vertical orientation, set ``horizontal``
     to False, defaults to True
    :param Boolean flip: Setting ``flip`` to True will flip the on and off
     direction, default is True
    :param float anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor
     point relative to the switch bounding box, default is None
    :param int anchored_position: (x,y) pixel value for the location
     of the anchor_point, default is None
    :param fill_color_off: (*RGB tuple
     or 24-bit hex value*) switch off-state fill color, default is ``(66, 44, 66)`` gray.
    :param fill_color_on: (*RGB tuple
     or 24-bit hex value*) switch on-state fill color, default is ``(0, 100, 0)`` green.
    :param outline_color_off: (*RGB tuple
     or 24-bit hex value*) switch off-state outline color, default is ``(30, 30, 30)``
     dark gray.
    :param outline_color_on: (*RGB tuple
     or 24-bit hex value*) switch on-state outline color, default is ``(0, 60, 0)`` green
    :param background_color_off: (*RGB tuple
     or 24-bit hex value*) background off-state color, default is ``(255, 255, 255)`` white
    :param background_color_on: (*RGB tuple
     or 24-bit hex value*) background on-state color, default is ``(0, 60, 0)`` dark green
    :param background_outline_color_off: (*RGB tuple
     or 24-bit hex value*) background outline color in off-state, if set to None this
     will default to ``background_color_off``, default is None
    :param background_outline_color_on: (*RGB tuple
     or 24-bit hex value*) background outline color in on-state, if set to None this
     will default to ``background_color_on``, default is None
    :param int switch_stroke: outline stroke width for the switch and background,
     in pixels, default is 2
    :param int text_stroke: outline stroke width (in pixels) for the 0/1 text shape
     outlines, if set to None it will use the value for ``switch_stroke``, default
     value is None
    :param Boolean display_button_text: Set True to display the 0/1 text shapes
     on the sliding switch, set False to hide the 0/1 text shapes, default value is True
    :param float animation_time: time for the switching animation, in seconds, default
     value is 0.2 seconds.
    :param Boolean value: the initial value for the switch, default is False

    .. _links:

    **Sections: Description of the SwitchRound widget**
        - :ref:`Quickstart: Importing and using SwitchRound <switch_round_details>`
        - :ref:`Summary: SwitchRound Features and input variables <feature_summary>`
        - :ref:`Description of features <features>`
        - :ref:`Internal details: How the SwitchRound widget works <internals>`
        - :ref:`Group structure: Display elements that make up SwitchRound <group_structure>`
        - :ref:`Coordinate systems and use of anchor_point and anchored_position <coordinates>`
        - :ref:`The Widget construction sequence <construction>`
        - :ref:`Making it move <move>`
        - :ref:`Orientation and a peculiarity of width and height definitions for
          SwitchRound <orientation>`
        - :ref:`Setting the touch response boundary <touch>`
        - :ref:`Summary and a final word <summary>`


    .. _switch_round_details:

    **Quickstart: Importing and using SwitchRound**

        Here is one way of importing the `SwitchRound` class so you can use it as
        the name ``Switch``:

        .. code-block:: python

            from adafruit_displayio_layout.widgets.switch_round import SwitchRound as Switch

        Now you can create a switch at pixel position x=20, y=30 using:

        .. code-block:: python

            my_switch=Switch(20, 30) # instance the switch at x=20, y=30

        Once you setup your display, you can now add ``my_switch`` to your display using:

        .. code-block:: python

            display.show(my_switch) # add the group to the display

        If you want to have multiple display elements, you can create a group and then
        append the switch and the other elements to the group.  Then, you can add the full
        group to the display as in this example:

        .. code-block:: python

            my_switch = Switch(20, 30) # instance the switch at x=20, y=30
            my_group = displayio.Group() # make a group
            my_group.append(my_switch) # Add my_switch to the group

            #
            # Append other display elements to the group
            #

            display.show(my_group) # add the group to the display

        For a full example, including how to respond to screen touches, check out the
        following examples in the `Adafruit_CircuitPython_DisplayIO_Layout
        <https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout>`_ library:

        - ``examples/displayio_layout_switch_simpletest.py`` and
        - ``examples/displayio_layout_switch_multiple.py``


    .. _feature_summary:

    **Summary: SwitchRound Features and input variables**

    The `SwitchRound` widget has numerous options for controlling its position, visible appearance,
    orientation, animation speed and value through a collection of input variables:

        - **position**: ``x``, ``y`` or ``anchor_point`` and ``anchored_position``


        - **size**: ``width`` and ``height`` (recommend to leave ``width`` = None to use
          preferred aspect ratio)

        - **orientation and movement direction (on vs. off)**: ``horizontal`` and ``flip``

        - **switch color**: ``fill_color_off``, ``fill_color_on``, ``outline_color_off`` and
          ``outline_color_on``

        - **background color**: ``background_color_off``, ``background_color_on``,
          ``background_outline_color_off``, and ``background_outline_color_on``

        - **linewidths**: ``switch_stroke`` and ``text_stroke``

        - **0/1 display**: Set ``display_button_text`` = True if you want the 0/1 shapes
          to show on the switch

        - **animation**: Set ``animation_time`` to the duration (in seconds) it will take
          to transition the switch, set zero if you want it to snap into position immediately
          (0.2 seconds is a good starting point, and larger values for bigger switches)

        - **value**: Set ``value`` to the initial value (True or False)

        - **touch boundaries**: ``touch_padding`` defines the number of additional pixels
          surrounding the switch that should respond to a touch.  (Note: The ``touch_padding``
          variable updates the ``touch_boundary`` Control class variable.  The definition of
          the ``touch_boundary`` is used to determine the region on the Widget that returns
          `True` in the `contains` function.)

    .. _features:

    **Description of features**

        The `SwitchRound` widget is a sliding switch that changes state whenever it is
        touched.  The color gradually changes from the off-state color scheme to the
        on-state color scheme as the switch transfers from off to the on position.
        The switch has an optional display of "0" and "1" on the sliding switch.  The
        switch can be oriented using the ``horizontal`` input variable, and the sliding
        direction can be changed using the ``flip`` input variable.

        Regarding switch sizing, it is recommended to set the height dimension but to
        leave the ``width = None``.  Setting ``width = None`` will allow the width to resize
        to maintain a recommended aspect ratio of width/height.  Alternately, the switch
        can be resized using the `resize` command, and it will adjust the width and height
        to the maximum size that will fit inside the requested width and height dimensions,
        while keeping the preferred aspect ratio.  To make the switch easier to be selected,
        additional padding around the switch can be defined using the ``touch_padding`` input
        variable to increase the touch-responsive area. The duration of
        animation between on/off can be set using the ``animation_time`` input variable.

    .. _internals:

    **Internal details: How the SwitchRound widget works**

    The `SwitchRound` widget is a graphical element that responds to touch elements
    to provide sliding switch on/off behavior.  Whenever touched, the switch toggles
    to its alternate value. The following sections describe the construction of the
    `SwitchRound` widget, in the hopes that it will serve as a first example of the key
    properties and responses for widgets.

    The `SwitchRound` widget inherits from two classes, it is a subclass of `Widget` (which
    itself is a subclass of `displayio.Group`) and a subclass of `Control`.  The `Widget`
    class helps define the positioning and sizing of the switch, while the `Control` class
    helps define the touch-response behavior.

    The following several sections describe the structure and inner workings of `SwitchRound`.

    .. _group_structure:

    **Group structure: Display elements that make up SwitchRound**

        The `Widget` class is a subclass of `displayio.Group`, thus we can append graphical
        elements to the Widget for displaying on the screen.  The switch consists of the
        following graphical elements:

        0. switch_roundrect: The switch background
        1. switch_circle: The switch button that slides back and forth
        2. Optional: text_0: The "0" circle shape on the switch button
        3. Optional: text_1: The "1" rectangle shape on the switch button

        The optional text items can be displayed or hidden using the ``display_button_text``
        input variable.

    .. _coordinates:

    **Coordinate systems and use of anchor_point and anchored_position**

        See the `Widget` class definition for clarification on the methods for positioning
        the switch, including the difference in the display coordinate system and the Widget's
        local coordinate system.

    .. _construction:

    **The Widget construction sequence**

        Here is the set of steps used to define this sliding switch widget.

        1. Initialize the stationary display items
        2. Initialize the moving display elements
        3. Store initial position of the moving display elements
        4. Define "keyframes" to determine the translation vector
        5. Define the ``_draw_position`` function between 0.0 to 1.0 (and slightly beyond)
        6. Select the motion "easing" function
        7. **Extra**. Go check out the ``_animate_switch`` method

        First, the stationary background rounded rectangle (RoundRect is created).  Second,
        the moving display elements are created, the circle for the switch, the circle for
        the text "0" and the rectangle for the text "1". Note that either the "0" or "1" is
        set as hidden, depending upon the switch value.  Third, we store away the
        initial position of the three moving elements, these initial values will be used in the
        functions that move these display elements.  Next, we define the motion of the
        moving element, by setting the ``self._x_motion`` and ``self._y_motion`` values
        that depending upon the ``horizontal`` and ``flip`` variables. These motion variables
        set the two "keyframes" for the moving elements, basically the endpoints of the switch
        motion.  (Note: other widgets may need an ``_angle_motion`` variable if they require
        some form of rotation.)  Next, we define the ``_draw_function`` method.  This method
        takes an input between 0.0 and 1.0 and adjusts the position relative to the motion
        variables, where 0.0 is the initial position and 1.0 represents the final position
        (as defined by the ``_x_motion`` and ``_y_motion`` values).  In the case of the
        sliding switch, we also use this ``position`` value (0.0 to 1.0) to gradually
        grade the color of the components between their "on" and "off" colors.

    .. _move:

    **Making it move**

        Everything above has set the ground rules for motion, but doesn't cause it to move.
        However, you have set almost all the pieces in place to respond to requests to change
        the position.  All that is left is the **Extra** method that performs the animation,
        called ``_animate_switch``. The ``_animate_switch`` method is triggered by a touch
        event through the ``selected`` Control class method.  Once triggered, this method
        checks how much time has elapsed.  Based on the elapsed time and the ``animation_time``
        input variable, the ``_animate_switch`` function calculates the ``position`` where
        the switch should be.  Then, it takes this ``position`` to call the ``_draw_position``
        method that will update the display elements based on the requested position.

        But there's even one more trick to the animation.  The ``_animate_switch`` calculates
        the target position based on a linear relationship between the time and the position.
        However, to give the animation a better "feel", it is desirable to tweak the motion
        function depending upon how this widget should behave or what suits your fancy. To
        do this we can use an "easing" function.  In short, this adjusts the constant speed
        (linear) movement to a variable speed during the movement.  Said another way, it
        changes the position versus time function according to a specific waveform equation.
        There are a lot of different "easing" functions that folks have used or you can make
        up your own.  Some common easing functions are provided in the ``easing.py`` file.
        You can change the easing function based on changing which function is imported
        at the top of this file. You can see where the position is tweaked by the easing
        function in the line in the ``_animate_switch`` method:

        .. code-block:: python

            self._draw_position(easing(position))  # update the switch position

        Go play around with the different easing functions and observe how the motion
        behavior changes.  You can use these functions in multiple dimensions to get all
        varieties of behavior that you can take advantage of.  The website
        `easings.net <https://easings.net>`_ can help you
        visualize some of the behavior of the easing functions.

    .. note:: Some of the "springy" easing functions require position values
            slightly below 0.0 and slightly above 1.0, so if you want to use these, be sure
            to check that your ``_draw_position`` method behaves itself for that range
            of position inputs.

    .. _orientation:

    **Orientation and a peculiarity of width and height definitions for SwitchRound**

        In setting the switch sizing, use height and width to set the narrow and wide
        dimension of the switch.  To try and reduce confusion, the orientation is modified
        after the height and width are selected.  That is, if the switch is set to vertical,
        the height and still mean the "narrow" and the width will still mean the dimensions
        in the direction of the sliding.

        If you need the switch to fit within a specific bounding box, it's preferred to use
        the ``resize`` function.  This will put the switch (in whatever orientation) at the
        maximum size where it can fit within the bounding box that you specified.  The switch
        aspect ratio will remain at the "preferred" aspect ratio of of 2:1 (width to height)
        after the resizing.

    .. _touch:

    **Setting the touch response boundary**

        The touch response area is defined by the Control class variable called
        ``touch_boundary``. In the case of the `SwitchRound` widget, we provide an
        ``touch_padding`` input variable.  The use of ``touch_padding`` defines an
        additional number of pixels surrounding the display elements that respond to touch
        events.  To achieve this additional space, the ``touch_boundary`` increases in size
        in all dimensions by the number of pixels specified in the ``touch_padding`` parameter.

        The ``touch_boundary`` is used in the Control function ``contains`` that checks
        whether any touch_points are within the boundary. Please pay particular attention to
        the `SwitchRound` contains function, since it calls the `Control.contains` superclass
        function with the touch_point value adjusted for the switch's ``.x`` and ``.y`` values.
        This offset adjustment is required since the `Control.contains` function operates only
        on the widget's local coordinate system.  It's good to keep in mind which coordinate
        system you are working in, to ensure your code responds to the right inputs!

    .. _summary:

    **Summary**

        The `SwitchRound` widget is an example to explain the use of the `Widget` and `Control`
        class functions.  The `Widget` class handles the overall sizing and positioning function
        and is the group that holds all the graphical elements.  The `Control` class is used to
        define the response of the widget to touch events (or could be generalized to other
        inputs).  Anything that only displays (such as a graph or an indicator light) won't
        need to inherit the `Control` class.  But anything that responds to touch inputs should
        inherit the `Control` class to define the ``touch_boundary`` and the touch response
        functions.

        I hope this `SwitchRound` widget will help turn on some new ideas and highlight some
        of the new capabilities of the `Widget` and `Control` classes.  Now go see what else
        you can create and extend from here!

    **A Final Word**

    The design of the Widget and Control classes are open for inputs.  If you think
    a additions or changes are useful, add it and please submit a pull request so
    others can use it too!  Also, keep in mind you don't even need to follow these classes
    to get the job done.  The Widget and Class definitions are designed to give guidance
    about one way to make things work, and to try to share some code.  If it's standing in
    your way, do something else!  If you want to use the ``grid_layout`` or other layout tools
    in this library, you only *really* need to have methods for positioning and resizing.

    .. note:: **Never let any of these class definitions hold you back, let your imagination run
        wild and make some cool widgets!**


    .. _methods:

    **SwitchRound methods**

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
        flip=False,  # flip the direction of the switch movement
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
        value=False,  # initial value
        **kwargs,
    ):

        # initialize the Widget superclass (x, y, scale)
        super().__init__(x=x, y=y, height=height, width=width, **kwargs)
        # Group elements for SwitchRound:
        #  0. switch_roundrect: The switch background
        #  1. switch_circle: The switch button
        #  2. Optional: text_0: The "0" circle on the switch button
        #  3. Optional: text_1: The "1" rectangle  on the switch button

        # initialize the Control superclass

        # pylint: disable=bad-super-call
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
            print("width set!")

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
        x_offset, y_offset, _ = self._get_offset_position(
            position
        )  # ignore angle_offset

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

            # Determines the direction of movement, depending upon if the
            # switch is going from on->off or off->on

            # constrain the elapsed time
            elapsed_time = time.monotonic() - start_time
            if elapsed_time > self._animation_time:
                elapsed_time = self._animation_time

            if self._value:
                position = (
                    1 - (elapsed_time) / self._animation_time
                )  # fraction from 0 to 1
            else:
                position = (elapsed_time) / self._animation_time  # fraction from 0 to 1

            # Update the moving elements based on the current position
            # apply the "easing" function to the requested position to adjust motion
            self._draw_position(easing(position))  # update the switch position

            # update the switch value once the motion is complete
            if (position >= 1) and not self._value:
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
