import time
from adafruit_display_shapes.triangle import Triangle
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.control import Control
from adafruit_display_text import label


class FlipInput(Widget, Control):
    def __init__(
        self,
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
        **kwargs,
    ):

        super().__init__(**kwargs, max_size=4)
        # Group elements for the FlipInput.
        # 1. The text
        # 2. Up arrow: Triangle
        # 3. Down arrow: Triangle

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
                    right = xposition + glyph.dx + glyph.width
                else:
                    right = max(right, xposition + glyph.dx + glyph.width)

                if top is None:
                    top = -(glyph.height + glyph.dy)
                else:
                    top = min(top, -(glyph.height + glyph.dy))

                if bottom is None:
                    bottom = -glyph.dy
                else:
                    bottom = max(bottom, -glyph.dy)

                xposition = xposition + glyph.shift_x

        self._bounding_box = [0, 0, right - left, bottom - top]

        # Create the text label

        self._label = label.Label(
            text=value_list[value],
            font=self._font,
            color=self._color,
            base_alignment=True,
        )
        self._label.x = -left
        self._label.y = -top

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

        self.append(self._label)  # add the label to the self Group

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

    def _update_value(self, new_value):
        # Could add animation here
        self._label.text = str(self.value_list[new_value])
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
    def value(self, new_value):
        new_value = new_value % len(self.value_list)
        self._update_value(new_value)
        self._value = new_value
