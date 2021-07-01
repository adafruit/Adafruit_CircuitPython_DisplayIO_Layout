# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
"""

`flip_input`
================================================================================
A flip style input selector.

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

import gc
import time
import displayio
from terminalio import FONT

from adafruit_display_shapes.triangle import Triangle

from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.control import Control

# pylint: disable=reimported

# select the two "easing" functions to use for animations
from adafruit_displayio_layout.widgets.easing import back_easeinout as easein
from adafruit_displayio_layout.widgets.easing import back_easeinout as easeout

# pylint: disable=too-many-arguments, too-many-branches, too-many-statements
# pylint: disable=too-many-locals, too-many-instance-attributes


class FlipInput(Widget, Control):
    """A flip style input selector. The value changes based on touch inputs on the
    two halves of the indicator with optional arrows added.


    :param int x: pixel position
    :param int y: pixel position

    :param displayio.Display display: the display where the widget will be displayed
    :param value_list: the list of strings that will be displayed
    :type value_list: List[str]
    :param Font font: the font used for the text (defaults to ``terminalio.FONT``)
    :param int font_scale: the scaling of the font in integer values (default is 1)
    :param int color: the color used for the font (default is 0xFFFFFF)
    :param int value: the index into the value_list that is initially displayed
     (default is 0)

    :param int arrow_color: the color used for the arrow fill (default is 0x333333)
    :param int arrow_outline: the color used for the arrow outline (default is 0x555555)
    :param int arrow_height: the height of the arrows, in pixels (default is 30 pixels)
    :param int arrow_width: the width of the arrows, in pixels (default is 30 pixels)
    :param int arrow_gap: distance from text to the arrow, in pixels (default is 5),
     can also be a negative value
    :param int arrow_touch_padding: additional padding on the arrow sides of the
     widget where touch response is accepted, in pixels (default = 0)
    :param int alt_touch_padding: additional padding on the non-arrow sides of the
     widget where touch response is accepted, in pixels (default = 0)
    :param Boolean horizontal: set to `True` to display arrows are in the horizontal
     direction, set `False` for arrows in the vertical direction (default = `True`)
    :param float animation_time: duration for the animation during flipping between
     values, in seconds (default is 0.4 seconds), set to 0.0 or `None` for no animation.
    :param float cool_down: minimum duration between activations of the widget with a
     continuous pressing, this can be used to reduce the chance of accidental multiple
     activations, in seconds (default is 0.0 seconds, no delay).  Set to -1.0 to require
     the button be released and pressed again for activation (Note: This requires calling
     the ``released`` function prior to the next call to ``selected``.)

    """

    def __init__(
        self,
        display,
        *,
        value_list=None,
        font=FONT,
        font_scale=1,
        color=0xFFFFFF,
        value=0,  # initial value, index into the value_list
        arrow_touch_padding=0,  # additional touch padding on the arrow sides of the Widget
        arrow_color=0x333333,
        arrow_outline=0x555555,
        arrow_height=30,
        arrow_width=30,
        arrow_gap=5,
        alt_touch_padding=0,  # touch padding on the non-arrow sides of the Widget
        horizontal=True,
        animation_time=None,
        cool_down=0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        # Group elements for the FlipInput.
        # 0. The text
        # 1. The group holding the temporary scroll bitmap
        # 2. Up arrow: Triangle
        # 3. Down arrow: Triangle

        # initialize the Control superclass

        # pylint: disable=bad-super-call
        super(Control, self).__init__()

        self.value_list = value_list
        self._value = value

        self._color = color
        self._font = font
        self._font_scale = font_scale
        # preload the glyphs

        self._arrow_touch_padding = arrow_touch_padding
        self._alt_touch_padding = alt_touch_padding

        self._horizontal = horizontal
        self._display = display

        self._animation_time = animation_time
        self._cool_down = cool_down
        self._last_pressed = time.monotonic()
        self._pressed = False  # state variable

        # Find the maximum bounding box of the text and determine the
        # baseline (x,y) start point (top, left)

        left = None
        right = None
        top = None
        bottom = None

        for this_value in value_list:
            xposition = 0

            for i, character in enumerate(this_value):
                glyph = self._font.get_glyph(ord(character))

                if (
                    i == 0
                ):  # if it's the first character in the string, check the left value
                    if left is None:
                        left = glyph.dx
                    else:
                        left = min(left, glyph.dx)

                if right is None:
                    right = max(
                        xposition + glyph.dx + glyph.width, xposition + glyph.shift_x
                    )
                else:
                    right = max(
                        right,
                        xposition + glyph.dx + glyph.width,
                        xposition + glyph.shift_x,
                    )  # match bitmap_label

                if top is None:
                    top = -(glyph.height + glyph.dy)
                else:
                    top = min(top, -(glyph.height + glyph.dy))

                if bottom is None:
                    bottom = -glyph.dy
                else:
                    bottom = max(bottom, -glyph.dy)

                xposition = xposition + glyph.shift_x

        self._bounding_box = [
            0,
            0,
            (right - left) * self._font_scale,
            (bottom - top) * self._font_scale,
        ]

        # Create the text label
        self._label = bitmap_label.Label(
            text=value_list[value],
            font=self._font,
            scale=self._font_scale,
            color=self._color,
            base_alignment=True,
            background_tight=True,
        )
        self._label.x = -1 * left * self._font_scale
        self._label.y = -1 * top * self._font_scale

        self._left = left
        self._top = top

        self.append(self._label)  # add the label to the self Group

        # set the touch_boundary including the touch_padding
        self._arrow_gap = arrow_gap  # of pixel gap above/below label before the arrow

        if horizontal:  # horizontal orientation, add arrow padding to x-dimension and
            # alt_padding to y-dimension
            self.touch_boundary = [
                self._bounding_box[0]
                - self._arrow_gap
                - arrow_height
                - self._arrow_touch_padding,
                self._bounding_box[1] - self._alt_touch_padding,
                self._bounding_box[2]
                + 2 * (self._arrow_gap + arrow_height + self._arrow_touch_padding),
                self._bounding_box[3] + 2 * self._alt_touch_padding,
            ]
        else:  # vertical orientation, add arrow padding to y-dimension and
            # alt_padding to x-dimension
            self.touch_boundary = [
                self._bounding_box[0] - self._alt_touch_padding,
                self._bounding_box[1]
                - self._arrow_gap
                - arrow_height
                - self._arrow_touch_padding,
                self._bounding_box[2] + 2 * self._alt_touch_padding,
                self._bounding_box[3]
                + 2 * (self._arrow_gap + arrow_height + self._arrow_touch_padding),
            ]

        # create the Up/Down arrows
        self._update_position()  # call Widget superclass function to reposition

        self._animation_group = displayio.Group(
            scale=self._font_scale
        )  # holds the animation bitmap
        # self._animation_group.x = -1 * left * (1)
        # self._animation_group.y = -1 * top * (1)
        self._animation_group.hidden = True
        self.append(self._animation_group)

        # Add the two arrow triangles, if required

        if (arrow_color is not None) or (arrow_outline is not None):

            if horizontal:  # horizontal orientation, add left and right arrows

                if (
                    (arrow_width is not None)
                    and (arrow_height is not None)
                    and (arrow_width > 0)
                ):
                    mid_point_y = self._bounding_box[1] + self._bounding_box[3] // 2
                    self.append(
                        Triangle(
                            self._bounding_box[0] - self._arrow_gap,
                            mid_point_y - arrow_height // 2,
                            self._bounding_box[0] - self._arrow_gap,
                            mid_point_y + arrow_height // 2,
                            self._bounding_box[0] - self._arrow_gap - arrow_width,
                            mid_point_y,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )

                    self.append(
                        Triangle(
                            self._bounding_box[0]
                            + self._bounding_box[2]
                            + self._arrow_gap,
                            mid_point_y - arrow_height // 2,
                            self._bounding_box[0]
                            + self._bounding_box[2]
                            + self._arrow_gap,
                            mid_point_y + arrow_height // 2,
                            self._bounding_box[0]
                            + self._bounding_box[2]
                            + self._arrow_gap
                            + arrow_width,
                            mid_point_y,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )
            else:  # vertical orientation, add upper and lower arrows

                if (
                    (arrow_height is not None)
                    and (arrow_width is not None)
                    and (arrow_height > 0)
                ):
                    mid_point_x = self._bounding_box[0] + self._bounding_box[2] // 2
                    self.append(
                        Triangle(
                            mid_point_x - arrow_width // 2,
                            self._bounding_box[1] - self._arrow_gap,
                            mid_point_x + arrow_width // 2,
                            self._bounding_box[1] - self._arrow_gap,
                            mid_point_x,
                            self._bounding_box[1] - self._arrow_gap - arrow_height,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )
                    self.append(
                        Triangle(
                            mid_point_x - arrow_width // 2,
                            self._bounding_box[1]
                            + self._bounding_box[3]
                            + self._arrow_gap,
                            mid_point_x + arrow_width // 2,
                            self._bounding_box[1]
                            + self._bounding_box[3]
                            + self._arrow_gap,
                            mid_point_x,
                            self._bounding_box[1]
                            + self._bounding_box[3]
                            + self._arrow_gap
                            + arrow_height,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )

    # Draw function to update the current value
    def _update_value(self, new_value, animate=True):

        if (
            (self._animation_time is not None)
            and (self._animation_time > 0)  # If animation is required
            and (animate)
        ):

            if ((new_value - self.value) == 1) or (
                (self.value == (len(self.value_list) - 1)) and (new_value == 0)
            ):  # wrap around
                start_position = 0.0
                end_position = 1.0
            else:
                start_position = 1.0
                end_position = 0.0

            self._display.auto_refresh = False

            gc.collect()

            # create the animation bitmap
            animation_bitmap = displayio.Bitmap(
                self._bounding_box[2] // self._font_scale,
                self._bounding_box[3] // self._font_scale,
                2,
            )  # color depth 2

            palette = displayio.Palette(2)
            palette.make_transparent(0)
            palette[1] = self._color
            animation_tilegrid = displayio.TileGrid(
                animation_bitmap, pixel_shader=palette
            )

            # add bitmap to the animation_group
            self._animation_group.append(animation_tilegrid)

            # store away the initial starting bitmap
            start_bitmap = displayio.Bitmap(
                self._label.bitmap.width, self._label.bitmap.height, 2
            )  # color depth 2
            start_bitmap.blit(0, 0, self._label.bitmap)

            # get the bitmap1 position offsets
            bitmap1_offset = [
                -1 * self._left + self._label.tilegrid.x,
                -1 * self._top + self._label.tilegrid.y,
            ]

            # hide the label group
            self.pop(0)

            # update the value label and get the bitmap offsets
            self._label.text = str(self.value_list[new_value])
            bitmap2_offset = [
                -1 * self._left + self._label.tilegrid.x,
                -1 * self._top + self._label.tilegrid.y,
            ]

            # animate between old and new bitmaps
            _animate_bitmap(
                display=self._display,
                target_bitmap=animation_bitmap,
                bitmap1=start_bitmap,
                bitmap1_offset=bitmap1_offset,
                bitmap2=self._label.bitmap,
                bitmap2_offset=bitmap2_offset,
                start_position=start_position,
                end_position=end_position,
                animation_time=self._animation_time,
                horizontal=self._horizontal,
            )

            # unhide the label group
            self.insert(0, self._label)

            # hide the animation group
            self._animation_group.pop()
            # free up memory
            del animation_bitmap
            del start_bitmap
            gc.collect()

            # ensure the display will auto_refresh (likely redundant)
            self._display.auto_refresh = True

        else:  # Update with no animation
            self._display.auto_refresh = False
            self._label.text = str(self.value_list[new_value])
            self._display.auto_refresh = True
        self._update_position()  # call Widget superclass function to reposition

    def _ok_to_change(self):  # checks state variable and timers to determine
        # if an update is allowed
        if self._cool_down < 0:  # if cool_down is negative, require ``released``
            # to be called before next change
            return not self._pressed
        if (time.monotonic() - self._last_pressed) < self._cool_down:
            return False  # cool_down time has not transpired
        return True

    def contains(self, touch_point):  # overrides, then calls Control.contains(x,y)
        """Returns True if the touch_point is within the widget's touch_boundary."""

        ######
        #
        # IMPORTANT: The touch_point should be adjusted to local coordinates, by
        # offsetting for self.x and self.y before calling the Control superclass function
        #
        ######
        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        return super().contains((touch_x, touch_y, 0))

    def selected(self, touch_point):
        """Response function when the Control is selected.  Increases value when upper half
        is pressed and decreases value when lower half is pressed."""

        # Adjust for local position of the widget using self.x and self.y

        if self._ok_to_change():
            t_b = self.touch_boundary

            if self._horizontal:
                if (
                    t_b[0] <= (touch_point[0] - self.x) < (t_b[0] + t_b[2] // 2)
                ):  # in left half of touch_boundary
                    self.value = self.value - 1

                elif (
                    (t_b[0] + t_b[2] // 2)
                    <= (touch_point[0] - self.x)
                    <= (t_b[0] + t_b[2])
                ):  # in right half of touch_boundary
                    self.value = self.value + 1

            else:
                if (
                    t_b[1] <= (touch_point[1] - self.y) < (t_b[1] + t_b[3] // 2)
                ):  # in upper half of touch_boundary
                    self.value = self.value + 1

                elif (
                    (t_b[1] + t_b[3] // 2)
                    <= (touch_point[1] - self.y)
                    <= (t_b[1] + t_b[3])
                ):  # in lower half of touch_boundary
                    self.value = self.value - 1

            self._pressed = True  # update the state variable
            self._last_pressed = (
                time.monotonic()
            )  # value changed, so update cool_down timer

    def released(self):
        """Response function when the Control is released. Resets the state variables
        for handling situation when ``cool_down`` is < 0 that requires `released()` before
        reacting another another `selected()`."""
        self._pressed = False

    @property
    def value(self):
        """The value index displayed on the widget. For the setter, the input can
         either be an `int` index into the ``value_list`` or
         can be a `str` that matches one of the items in the ``value_list``.  If `int`,
         the value will be set based on the modulus of the input ``new_value``.

        :return: int
        """

        return self._value

    @value.setter
    def value(self, new_value):  # Set the value based on the index or on the string.
        if isinstance(new_value, str):  # for an input string, search the value_list
            try:
                new_value = self.value_list.index(new_value)
            except ValueError:
                print(
                    'ValueError: Value "{}" not found in value_list.'.format(new_value)
                )
                return None

        new_value = new_value % len(self.value_list)  # Update the value
        if new_value != self._value:
            self._update_value(new_value)
            self._value = new_value
        return self._value


# draw_position - Draws two bitmaps into the target bitmap with offsets.
# Allows values < 0.0 and > 1.0 for "springy" easing functions
def _draw_position(
    target_bitmap,
    bitmap1,
    bitmap1_offset,
    bitmap2,
    bitmap2_offset,
    position=0.0,
    horizontal=True,
):

    x_offset1 = bitmap1_offset[0]
    y_offset1 = bitmap1_offset[1]
    x_offset2 = bitmap2_offset[0]
    y_offset2 = bitmap2_offset[1]

    if position == 0.0:
        target_bitmap.fill(0)
        target_bitmap.blit(x_offset1, y_offset1, bitmap1)
        return
    if position == 1.0:
        target_bitmap.fill(0)
        target_bitmap.blit(x_offset2, y_offset2, bitmap2)
        return

    if horizontal:
        target_bitmap.fill(0)  # clear the target bitmap
        x_index = round(position * target_bitmap.width)  # find the scroll offset
        _blit_constrained(target_bitmap, x_offset1, y_offset1, bitmap1, x1=x_index)
        _blit_constrained(
            target_bitmap,
            target_bitmap.width - x_index + x_offset2,
            y_offset2,
            bitmap2,
            x1=0,
            x2=x_index,
        )

    else:
        target_bitmap.fill(0)
        y_index = round(position * target_bitmap.height)

        _blit_constrained(target_bitmap, x_offset1, y_offset1, bitmap1, y1=y_index)
        _blit_constrained(
            target_bitmap,
            x_offset2,
            target_bitmap.height - y_index + y_offset2,
            bitmap2,
            y1=0,
            y2=y_index,
        )


# pylint: disable=invalid-name

# _blit_constrained: Copies bitmaps with constraints to the dimensions
def _blit_constrained(target, x, y, source, x1=None, y1=None, x2=None, y2=None):
    if x1 is None:
        x1 = 0
    if y1 is None:
        y1 = 0
    if x2 is None:
        x2 = source.width
    if y2 is None:
        y2 = source.height

    if x < 0:
        x1 -= x  # offset the clip region in positive direction
        x2 -= x
        x = 0
    if x1 < 0:
        x = x - x1
        x1 = 0  # move to origin
    if x2 > source.width:
        x2 = source.width

    if y < 0:
        y1 -= y  # offset the clip region
        y2 -= y
        y = 0
    if y1 < 0:
        y = y - y1
        y1 = 0
    if y2 > source.height:
        y2 = source.height

    if (
        (x > target.width)
        or (y > target.height)
        or (x1 > source.width)
        or (y1 > source.height)
    ):
        return

    target.blit(x, y, source, x1=x1, y1=y1, x2=x2, y2=y2)


# _animate_bitmap - performs animation of scrolling between two bitmaps
def _animate_bitmap(
    display,
    target_bitmap,
    bitmap1,
    bitmap1_offset,
    bitmap2,
    bitmap2_offset,
    start_position,
    end_position,
    animation_time,
    horizontal,
):

    start_time = time.monotonic()

    if start_position > end_position:  # direction is decreasing: "out"
        [bitmap2, bitmap1] = [bitmap1, bitmap2]
        [bitmap2_offset, bitmap1_offset] = [bitmap1_offset, bitmap2_offset]
        easing_function = easeout  # use the "out" easing function

    else:  # direction is increasing: "in"
        easing_function = easein  # use the "in" easing function

    display.auto_refresh = False
    _draw_position(
        target_bitmap,
        bitmap1,
        bitmap1_offset,
        bitmap2,
        bitmap2_offset,
        position=start_position,
        horizontal=horizontal,
    )
    display.auto_refresh = True

    while True:

        this_time = time.monotonic()
        target_position = (
            start_position
            + (end_position - start_position)
            * (this_time - start_time)
            / animation_time
        )

        display.auto_refresh = False
        if (this_time - start_time) < animation_time:
            display.auto_refresh = False
            _draw_position(
                target_bitmap,
                bitmap1,
                bitmap1_offset,
                bitmap2,
                bitmap2_offset,
                position=easing_function(target_position),
                horizontal=horizontal,
            )
            display.auto_refresh = True
        else:

            _draw_position(
                target_bitmap,
                bitmap1,
                bitmap1_offset,
                bitmap2,
                bitmap2_offset,
                position=end_position,
                horizontal=horizontal,
            )

            break
        display.auto_refresh = True
    display.auto_refresh = True
