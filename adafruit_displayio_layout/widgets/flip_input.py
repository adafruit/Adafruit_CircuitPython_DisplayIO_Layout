import time
from adafruit_display_shapes.triangle import Triangle
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.control import Control
from adafruit_display_text import bitmap_label
from adafruit_display_text import label
import displayio
import gc
import adafruit_displayio_layout.widgets.easing as easing


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


# draw_position - Allows values < 0.0 and > 1.0 for "springy" easing functions


def draw_position(
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

    # print('position: {}'.format(position))

    if position == 0.0:
        target_bitmap.fill(0)
        target_bitmap.blit(x_offset1, y_offset1, bitmap1)
        return
    if position == 1.0:
        target_bitmap.fill(0)
        target_bitmap.blit(x_offset2, y_offset2, bitmap2)
        return

    if horizontal:
        target_bitmap.fill(0)
        x_index = round(position * target_bitmap.width)
        blit_constrained(target_bitmap, x_offset1, y_offset1, bitmap1, x1=x_index)
        blit_constrained(
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

        blit_constrained(target_bitmap, x_offset1, y_offset1, bitmap1, y1=y_index)
        blit_constrained(
            target_bitmap,
            x_offset2,
            target_bitmap.height - y_index + y_offset2,
            bitmap2,
            y1=0,
            y2=y_index,
        )


def blit_constrained(target, x, y, source, x1=None, y1=None, x2=None, y2=None):
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


def animate_bitmap(
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
    easing_functions=[
        easing.LinearInterpolation,
        easing.LinearInterpolation,
    ],  # in, out
):
    import time

    # print("start_pos: {}, end_pos: {}".format(start_position, end_position))
    max_position = max(start_position, end_position)
    min_position = min(start_position, end_position)
    start_time = time.monotonic()

    if start_position > end_position:  # direction is decreasing: "out"
        temp = bitmap2
        bitmap2 = bitmap1
        bitmap1 = temp

        temp_offset = bitmap2_offset
        bitmap2_offset = bitmap1_offset
        bitmap1_offset = temp_offset

        easing_function = easing_functions[1]  # use the "out" easing function

    else:  # direction is increasing: "in"
        easing_function = easing_functions[0]  # use the "in" easing function

    display.auto_refresh = False
    draw_position(
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

        target_position = (
            start_position
            + (end_position - start_position)
            * (time.monotonic() - start_time)
            / animation_time
        )

        display.auto_refresh = False
        if min_position < target_position < max_position:
            display.auto_refresh = False
            draw_position(
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

            draw_position(
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


class FlipInput(Widget, Control):
    def __init__(
        self,
        display,
        value_list=None,
        font=None,
        color=0xFFFFFF,
        value=0,  # initial value, index into the value_list
        debug=False,
        arrow_touch_padding=0,  # touch padding on the arrow sides of the Widget
        arrow_color=None,
        arrow_outline=None,
        arrow_height=None,
        arrow_width=None,
        alt_touch_padding=0,  # touch padding on the non-arrow sides of the Widget
        horizontal=True,
        animation_time=None,
        easing_mode=None,
        **kwargs,
    ):

        super().__init__(**kwargs, max_size=5)
        # Group elements for the FlipInput.
        # 1. The text
        # 2. The group holding the temporary scroll bitmap
        # 3. Up arrow: Triangle
        # 4. Down arrow: Triangle

        # initialize the Control superclass
        super(Control, self).__init__()

        self.value_list = value_list
        self._value = value

        self._color = color
        self._font = font
        # preload the glyphs

        self._arrow_touch_padding = arrow_touch_padding
        self._alt_touch_padding = alt_touch_padding

        self._horizontal = horizontal
        self._display = display

        self._animation_time = animation_time

        self._easing_mode = easing_mode

        # `easing_dict` is the mapping function for the easing_mode string input
        # and translating to the "easing" animation motion functions, see `widgets/easing.py`
        easing_dict = {
            "linear": [easing.LinearInterpolation, easing.LinearInterpolation],
            "quadratic": [easing.QuadraticEaseIn, easing.QuadraticEaseOut],
            "cubic": [easing.CubicEaseIn, easing.CubicEaseOut],
            "quartic": [easing.QuarticEaseIn, easing.QuarticEaseOut],
            "quintic": [easing.QuinticEaseIn, easing.QuinticEaseOut],
            "sine": [easing.SineEaseIn, easing.SineEaseOut],
            "circular": [easing.CircularEaseIn, easing.CircularEaseOut],
            "exponential": [easing.ExponentialEaseIn, easing.ExponentialEaseOut],
            "elastic": [easing.ElasticEaseInOut, easing.ElasticEaseInOut],
            "back": [easing.BackEaseIn, easing.BackEaseOut],
            "bounce": [easing.BounceEaseIn, easing.BounceEaseOut],
        }

        print("easing_mode: {}".format(self._easing_mode))
        try:
            self._easing_functions = easing_dict[
                (self._easing_mode).lower()
            ]  # convert to lower case
        except:  # default to Linear interpolation
            print("easing_mode not found: Defaulting to LinearInterpolation.")
            self._easing_functions = [
                easing.LinearInterpolation,
                easing.LinearInterpolation,
            ]

        # Find the maximum bounding box of the text and determine the baseline (x,y) start point (top, left)

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
                # print("left, right, top, bottom: {},{}, {},{}, new x_position".format(left,right,top,bottom, xposition))

        self._bounding_box = [0, 0, right - left, bottom - top]
        # print("bounding_box: {}".format(self._bounding_box))

        # Create the text label

        self._label = bitmap_label.Label(
            text=value_list[value],
            font=self._font,
            color=self._color,
            base_alignment=True,
            background_tight=True,
        )
        self._label.x = -left
        self._label.y = -top

        self.append(self._label)  # add the label to the self Group

        # self._update_value(self._value)

        # set the touch_boundary including the touch_padding

        if (
            horizontal
        ):  # horizontal orientation, add arrow padding to x-dimension and alt_padding to y-dimension
            self.touch_boundary = [
                self._bounding_box[0] - self._arrow_touch_padding,
                self._bounding_box[1] - self._alt_touch_padding,
                self._bounding_box[2] + 2 * self._arrow_touch_padding,
                self._bounding_box[3] + 2 * self._alt_touch_padding,
            ]
        else:  # vertical orientation, add arrow padding to y-dimension and alt_padding to x-dimension
            self.touch_boundary = [
                self._bounding_box[0] - self._alt_touch_padding,
                self._bounding_box[1] - self._arrow_touch_padding,
                self._bounding_box[2] + 2 * self._alt_touch_padding,
                self._bounding_box[3] + 2 * self._arrow_touch_padding,
            ]

        # create the Up/Down arrows

        self._update_position()  # call Widget superclass function to reposition

        if debug:  # show the touch_bounding box
            from adafruit_display_shapes.rect import Rect

            self._rect = Rect(
                self.touch_boundary[0],
                self.touch_boundary[1],
                self.touch_boundary[2],
                self.touch_boundary[3],
                fill=0x222222,
            )
            self.append(self._rect)

        self._animation_group = displayio.Group(
            max_size=1
        )  # holds the animation bitmap
        self._animation_group.hidden = True
        self.append(self._animation_group)

        # Add the two arrow triangles, if required

        if (arrow_color is not None) or (arrow_outline is not None):
            gap = 5  # of pixel gap above/below label

            if horizontal:  # horizontal orientation, add left and right arrows
                if arrow_height is None:
                    arrow_height = self._bounding_box[3]
                if arrow_width is None:
                    arrow_width = arrow_touch_padding

                if arrow_width > 0:
                    mid_point_y = self._bounding_box[1] + self._bounding_box[3] // 2
                    self.append(
                        Triangle(
                            self._bounding_box[0] - gap,
                            mid_point_y - arrow_height // 2,
                            self._bounding_box[0] - gap,
                            mid_point_y + arrow_height // 2,
                            self._bounding_box[0] - gap - arrow_width,
                            mid_point_y,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )

                    self.append(
                        Triangle(
                            self._bounding_box[0] + self._bounding_box[2] + gap,
                            mid_point_y - arrow_height // 2,
                            self._bounding_box[0] + self._bounding_box[2] + gap,
                            mid_point_y + arrow_height // 2,
                            self._bounding_box[0]
                            + self._bounding_box[2]
                            + gap
                            + arrow_width,
                            mid_point_y,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )
            else:  # vertical orientation, add upper and lower arrows
                if arrow_height is None:
                    arrow_height = arrow_touch_padding
                if arrow_width is None:
                    arrow_width = self._bounding_box[2]

                if arrow_height > 0:
                    mid_point_x = self._bounding_box[0] + self._bounding_box[2] // 2
                    self.append(
                        Triangle(
                            mid_point_x - arrow_width // 2,
                            self._bounding_box[1] - gap,
                            mid_point_x + arrow_width // 2,
                            self._bounding_box[1] - gap,
                            mid_point_x,
                            self._bounding_box[1] - gap - arrow_height,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )
                    self.append(
                        Triangle(
                            mid_point_x - arrow_width // 2,
                            self._bounding_box[1] + self._bounding_box[3] + gap,
                            mid_point_x + arrow_width // 2,
                            self._bounding_box[1] + self._bounding_box[3] + gap,
                            mid_point_x,
                            self._bounding_box[1]
                            + self._bounding_box[3]
                            + gap
                            + arrow_height,
                            fill=arrow_color,
                            outline=arrow_outline,
                        )
                    )

        # Draw function of the current value

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
                self._bounding_box[2], self._bounding_box[3], 2
            )  # color depth 2

            # print("bounding_box: {}".format(self._bounding_box))
            palette = displayio.Palette(2)
            palette.make_transparent(0)
            palette[1] = self._color
            animation_tilegrid = displayio.TileGrid(
                animation_bitmap, pixel_shader=palette
            )

            # print("1 self._label.x,y: {},{} bitmap width, height: {}, {}, label.tilegrid x,y: {},{}".format(self._label.x, self._label.y, self._label.bitmap.width, self._label.bitmap.height, self._label.tilegrid.x, self._label.tilegrid.y))

            # blit current value bitmap into the animation bitmap
            # animation_bitmap.blit(0, 0, self._label.bitmap)
            # add bitmap to the animation_group
            self._animation_group.append(animation_tilegrid)

            # store away the initial starting bitmap
            start_bitmap = displayio.Bitmap(
                self._label.bitmap.width, self._label.bitmap.height, 2
            )  # color depth 2
            start_bitmap.blit(0, 0, self._label.bitmap)
            # get the bitmap1 position offsets
            bitmap1_offset = [
                self._label.x + self._label.tilegrid.x,
                self._label.y + self._label.tilegrid.y,
            ]

            # hide the label group.
            self.pop(0)

            # update the value label and get the bitmap offsets
            self._label.text = str(self.value_list[new_value])
            bitmap2_offset = [
                self._label.x + self._label.tilegrid.x,
                self._label.y + self._label.tilegrid.y,
            ]

            # animate between old and new bitmaps
            animate_bitmap(
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
                easing_functions=self._easing_functions,
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
        """Response function when Control is selected.  Increases value when upper half is pressed
        and decreases value when lower half is pressed."""

        # Adjust for local position of the widget using self.x and self.y

        tb = self.touch_boundary

        if self._horizontal:
            if (
                tb[0] <= (touch_point[0] - self.x) < (tb[0] + tb[2] // 2)
            ):  # in left half of touch_boundary
                self.value = self.value - 1

            elif (
                (tb[0] + tb[2] // 2) <= (touch_point[0] - self.x) <= (tb[0] + tb[2])
            ):  # in right half of touch_boundary
                self.value = self.value + 1

        else:
            if (
                tb[1] <= (touch_point[1] - self.y) < (tb[1] + tb[3] // 2)
            ):  # in upper half of touch_boundary
                self.value = self.value + 1

            elif (
                (tb[1] + tb[3] // 2) <= (touch_point[1] - self.y) <= (tb[1] + tb[3])
            ):  # in lower half of touch_boundary
                self.value = self.value - 1

    @property
    def value(self):
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
                return

        new_value = new_value % len(self.value_list)  # Update the value
        if new_value != self._value:
            self._update_value(new_value)
        self._value = new_value
