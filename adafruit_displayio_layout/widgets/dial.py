# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
"""

`dial`
================================================================================
A dial gauge widget for displaying graphical information.

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# pylint: disable=too-many-lines, too-many-instance-attributes, too-many-arguments
# pylint: disable=too-many-locals, too-many-statements


import math
import displayio
import vectorio

try:
    import bitmaptools
except NameError:
    pass  # utilize the blit_rotate_scale function defined herein


from terminalio import FONT as terminalio_FONT
from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.widgets.widget import Widget


class Dial(Widget):
    """A dial widget.  The origin is set using ``x`` and ``y``.

    :param int x: pixel position
    :param int y: pixel position

    :param int width: requested width, in pixels
    :param int height: requested height, in pixels
    :param int padding: keepout padding amount around the border, in pixels,
     default is 12

    :param float sweep_angle: dial rotation, in degrees, maximum value is 360 degrees,
     default is 90 degrees
    :param float start_angle: starting angle, in degrees.  Set to `None` for symmetry along
     vertical axis.  Vertical is defined as 0 degrees.
     Negative values are counter-clockwise degrees; positive values
     are clockwise degrees. Defaults to `None`.

    :param float min_value: the minimum value displayed on the dial, default is 0.0
    :param float max_value: the maximum value displayed the dial, default is 100.0
    :param float value: the value to display (if None, defaults to ``min_value``)

    :param Boolean display_value: set `True` to display a value label on the dial
    :param Font value_font: the font for the value label, defaults to
     ``terminalio.FONT``
    :param int value_color: the color for the value label, defaults to 0xFF0000
    :param str value_format_string: the format string for displaying the value label
     (defaults to ':0.0f' to show the value rounded to the nearest whole number)
    :param (float,float) value_label_anchor_point: anchor point on the label, default
     value is (0.5, -1.0) where the y-value of -1.0 signifies the text baseline
    :param (float,float) value_label_anchor_point_on_widget: anchor point on the
     widget where the label will be placed, default value is (0.5, 0.5)

    :param int needle_width: requested pixel width of the triangular needle,
     default = 7
    :param int needle_color: color value for the needle, defaults to red (0xFF0000)
    :param Boolean limit_rotation: Set True to limit needle rotation to between the
     ``min_value`` and ``max_value``, set to False for unlimited rotation, default is True

    :param int tick_color: tick line color (24-bit hex value), defaults to 0xFFFFFF
    :param int major_ticks: number of major ticks, default = 5
    :param int major_tick_stroke: major tick line stroke width, in pixels, default = 3
    :param int major_tick_length: major tick length, in pixels, default = 10
    :param str major_tick_labels: array of strings for the major tick labels,
     default is ("0", "25", "50", "75", "100")
    :param float tick_label_scale: the scaling of the tick labels, default = 1.0
    :param Font tick_label_font: font to be used for major tick labels, default
     is ``terminalio.FONT``
    :param int tick_label_color: color for the major tick labels, default is 0xFFFFFF
    :param Boolean angle_tick_labels: set True to rotate the major tick labels to
     match the tick angle, default is True

    :param int minor_ticks: number of minor ticks (per major tick), default = 5
    :param int minor_tick_stroke: minor tick line stroke width, in pixels, default = 1
    :param int minor_tick_length: minor tick length, in pixels, default = 5

    :param int background_color: background color (RGB tuple
     or 24-bit hex value), set `None` for transparent, default is `None`


    :param (float,float) anchor_point: (X,Y) values from 0.0 to 1.0 to define the dial's
     anchor point relative to the dial's bounding box
    :param (int,int) anchored_position: (x,y) pixel value for the location
     of the `anchor_point`


    **Simple example of dial and moving needle**

    See file: ``examples/displayio_layout_dial_simpletest.py``

    .. figure:: dial.gif
       :scale: 100 %
       :figwidth: 50%
       :align: center
       :alt: Diagram of the dial widget with needle in motion.

       This is a diagram of a dial widget with the needle moving from its
       minimum to maximum positions.

    .. figure:: dial_variables_angles.png
       :scale: 50 %
       :figwidth: 70%
       :align: center
       :alt: Diagram showing the definition of ``start_angle`` and ``sweep_angle``,
        both are in units of degrees.

       Diagram showing the definition of ``start_angle`` and ``sweep_angle``,
       both are in units of degrees.

    .. figure:: dial_variables_min_max_values.png
       :scale: 50 %
       :figwidth: 70%
       :align: center
       :alt: Diagram showing the defintion of ``min_value`` and ``max_value``.

       Diagram showing the defintion of ``min_value`` and ``max_value``.

    .. figure:: dial_variables_ticks.png
       :scale: 50 %
       :figwidth: 70%
       :align: center
       :alt: Diagram showing the various parameters for setting the dial labels
        and major and minor tick marks.

       Diagram showing the various parameters for setting the dial labels
       and major and minor tick marks.

    .. figure:: dial_variables_clip_needle.png
       :scale: 35 %
       :figwidth: 70%
       :align: center
       :alt: Diagram showing the impact of ``clip_needle`` Boolean value.

       Diagram showing the impact of the ``clip_needle`` input parameter,
       with the dial's boundary shown. For ``sweep_angle`` values less than
       180 degrees, the needle can protrude a long way from the dial ticks. By
       setting ``clip_needle = True``, the needle graphic will be clipped at the edge
       of the dial boundary (see comparison in the graphic above). The left dial is
       created with ``clip_needle = False``, meaning that the dial is not clipped.  The
       right dial is created with ``clip_needle = True`` and the needle is clipped at
       the edge of the dial.  Use additional ``padding`` to expose more length of
       needle, even when clipped.
    """

    # The dial is a subclass of Group->Widget.

    def __init__(
        self,
        width=100,
        height=100,
        padding=12,  # keepout amount around border, in pixels
        sweep_angle=90,  # maximum value is 180 degrees
        start_angle=None,
        clip_needle=False,
        # trims off the needle outside of the dial region, used for sweep_angles < 180
        needle_width=7,
        # triangle with this base width, best if this is odd
        needle_color=0x880000,
        limit_rotation=True,
        value=None,
        value_font=None,
        display_value=False,
        value_color=0xFF0000,
        value_format_string=":0.0f",
        min_value=0.0,
        max_value=100.0,
        anchor_point=None,
        anchored_position=None,
        tick_color=0xFFFFFF,
        major_ticks=5,  # if int, the total number of major ticks
        major_tick_stroke=3,
        major_tick_length=10,
        major_tick_labels=("0", "25", "50", "75", "100"),
        minor_ticks=5,  # if int, the number of minor ticks per major tick
        minor_tick_stroke=1,
        minor_tick_length=5,
        tick_label_font=None,
        tick_label_color=0xFFFFFF,
        rotate_tick_labels=True,
        tick_label_scale=1.0,
        background_color=None,
        value_label_anchor_point=(
            0.5,
            -1.0,
        ),  # default label position uses (x-center point, y-text baseline)
        value_label_anchor_on_widget=(0.5, 0.5),  # default label position on widget
        **kwargs,
    ):

        # initialize the Widget superclass (x, y, scale)
        super().__init__(**kwargs, max_size=3)
        # Define how many graphical elements will be in this group
        # using "max_size=XX"
        #
        # Group elements for SwitchRoundHorizontal:
        #  0. TileGrid holding bitmap with ticks and tick label text
        #  1. Value label (optional)
        #  2. Needle bitmap

        self._min_value = min_value
        self._max_value = max_value
        if value is None:  # if none, set to the minimum value
            self._value = self._min_value
        else:
            self._value = value

        if value_font is None:
            self._value_font = terminalio_FONT
        else:
            self._value_font = value_font
        self._value_color = value_color
        self._display_value = display_value
        self._value_format_string = value_format_string

        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        # validate sweep_angle and start_angle
        if sweep_angle > 360:
            raise ValueError("sweep_angle must be <= 360 degrees")

        sweep_angle = max(
            1, sweep_angle
        )  # constrain to >= 1 to avoid divide by zero errors
        self._sweep_angle = sweep_angle

        if start_angle is None:
            start_angle = -sweep_angle / 2
        elif not -360 <= start_angle <= 360:
            raise ValueError("start_angle must be between -360 and +360 degrees")
        self._start_angle = start_angle

        self._clip_needle = clip_needle
        self._needle_width_requested = needle_width
        self._needle_color = needle_color
        self._limit_rotation = limit_rotation
        self._background_color = background_color

        self._major_tick_labels = major_tick_labels

        self._tick_color = tick_color
        self._tick_label_color = tick_label_color
        if tick_label_font is None:
            self._tick_label_font = terminalio_FONT
        else:
            self._tick_label_font = tick_label_font
        self._tick_label_scale = tick_label_scale
        self._rotate_tick_labels = rotate_tick_labels

        self._major_ticks = major_ticks
        self._major_tick_stroke = major_tick_stroke
        self._major_tick_length = major_tick_length
        self._minor_ticks = minor_ticks
        self._minor_tick_stroke = minor_tick_stroke
        self._minor_tick_length = minor_tick_length

        self._label_anchor_point = value_label_anchor_point
        self._label_anchor_on_widget = value_label_anchor_on_widget

        self._padding = padding

        # initialize variables before creating the dial
        self._dial_center = None
        self._dial_radius = None
        self._trim_line = None
        self._needle_palette = None
        self._needle = None
        self._needle_vector_shape = None
        self._needle_width = None

        self._initialize_dial(width, height)

    def _initialize_dial(self, width, height):

        for _ in range(len(self)):
            self.pop()

        # get the tick label font height
        self._font_height = self._get_font_height(
            font=self._tick_label_font, scale=self._tick_label_scale
        )

        # update the dial dimensions to fit inside the requested width and height
        self._adjust_dimensions(width, height)
        self._bounding_box = [0, 0, self._width, self._height]
        self._update_position()

        # create the dial palette and bitmaps
        self.dial_bitmap = displayio.Bitmap(
            self._width, self._height, 3
        )  # 3 colors: background, ticks, tick label text

        # paint the dial major and minor ticks and labels
        draw_ticks(  # major ticks
            target_bitmap=self.dial_bitmap,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            tick_count=self._major_ticks,
            tick_stroke=self._major_tick_stroke,
            tick_length=self._major_tick_length,
            start_angle=self._start_angle,
            sweep_angle=self._sweep_angle,
            tick_color_index=2,
        )

        draw_ticks(  # minor ticks
            target_bitmap=self.dial_bitmap,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            tick_count=self._minor_ticks * (self._major_ticks - 1) + 1,
            tick_stroke=self._minor_tick_stroke,
            tick_length=self._minor_tick_length,
            start_angle=self._start_angle,
            sweep_angle=self._sweep_angle,
            tick_color_index=2,
        )

        draw_labels(
            target_bitmap=self.dial_bitmap,
            font=self._tick_label_font,
            tick_labels=self._major_tick_labels,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            start_angle=self._start_angle,
            sweep_angle=self._sweep_angle,
            rotate_labels=self._rotate_tick_labels,
            font_height=self._font_height,
            tick_label_scale=self._tick_label_scale,
        )

        # create the dial palette
        self.dial_palette = displayio.Palette(4)
        if self._background_color is None:
            self.dial_palette.make_transparent(0)
            self.dial_palette[0] = 0x000000
        else:
            self.dial_palette[0] = self._background_color
        self.dial_palette[1] = self._tick_label_color
        self.dial_palette[2] = self._tick_color

        # create the dial tilegrid and append to the self Widget->Group
        self.dial_tilegrid = displayio.TileGrid(
            self.dial_bitmap, pixel_shader=self.dial_palette
        )
        self.append(self.dial_tilegrid)

        # create the label for the display_value
        if self._display_value:
            self._value_label = bitmap_label.Label(
                self._value_font,
                text="",
                color=self._value_color,
                baseline_alignment=True,
            )
            self._value_label.anchor_point = self._label_anchor_point
            self._value_label.anchored_position = [
                round(self._width * self._label_anchor_on_widget[0]),
                round(self._height * self._label_anchor_on_widget[1]),
            ]
            self._update_value()
            self.append(self._value_label)

        # create the needle
        self._create_needle()
        self.append(self._needle_vector_shape)
        self._update_needle(self._value)

    def _adjust_dimensions(self, width, height):
        # get normalized dimensions of the dial based on start_angle and sweep_angle
        # in units of diameter

        # if the sweep angle is < 180, then adjust size if needle should clipped:
        if (self._sweep_angle < 180) and (self._clip_needle):
            [left, top, right, bottom, x_center_calc, y_center_calc] = _getCoords(
                [self._start_angle, self._start_angle + self._sweep_angle],
                ignore_center=True,
            )
        else:
            [left, top, right, bottom, x_center_calc, y_center_calc] = _getCoords(
                [self._start_angle, self._start_angle + self._sweep_angle]
            )

        # calculate the pixel dimension to fit within width/height (including padding)
        if (width - 2 * self._padding < 0) or (height - 2 * self._padding < 0):
            raise ValueError("Width, height, or padding size makes zero sized box")
        requested_aspect_ratio = (width - 2 * self._padding) / (
            height - 2 * self._padding
        )
        box_aspect_ratio = (right - left) / (bottom - top)

        if box_aspect_ratio >= requested_aspect_ratio:
            # keep width and adjust the width
            self._width = width
            self._height = math.ceil((width - 2 * self._padding) / box_aspect_ratio) + (
                2 * self._padding
            )
            radius = round((width - 2 * self._padding) / (2 * (right - left)))

        else:
            # keep height and adjust the width
            self._height = height
            self._width = math.ceil(
                ((height - 2 * self._padding) * box_aspect_ratio)
            ) + (2 * self._padding)
            radius = round((height - 2 * self._padding) / (2 * (bottom - top)))

        center_x = round(x_center_calc * radius * 2) + self._padding
        center_y = round(y_center_calc * radius * 2) + self._padding
        self._dial_center = (center_x, center_y)
        self._dial_radius = radius

        if self._clip_needle:  # define the line endpoints that will trim off the needle
            trim_x1 = round(
                center_x
                + math.sin(self._start_angle * 2 * math.pi / 360)
                * (self._dial_radius - self._padding)
            )
            trim_y1 = round(
                center_y
                - math.cos(self._start_angle * 2 * math.pi / 360)
                * (self._dial_radius - self._padding)
            )
            trim_x2 = round(
                center_x
                + math.sin((self._start_angle + self._sweep_angle) * 2 * math.pi / 360)
                * (self._dial_radius - self._padding)
            )
            trim_y2 = round(
                center_y
                - math.cos((self._start_angle + self._sweep_angle) * 2 * math.pi / 360)
                * (self._dial_radius - self._padding)
            )
            self._trim_line = [(trim_x1, trim_y1), (trim_x2, trim_y2)]
        else:
            self._trim_line = None

    def _get_font_height(self, font, scale):
        if (self._major_tick_labels == []) or (font is None):
            font_height = 0
        else:
            if hasattr(font, "get_bounding_box"):
                font_height = int(scale * font.get_bounding_box()[1])
            elif hasattr(font, "ascent"):
                font_height = int(scale * font.ascent + font.ascent)
        return font_height

    def _create_needle(self):
        # Create the needle
        self._needle_palette = displayio.Palette(2)
        self._needle_palette.make_transparent(0)
        self._needle_palette[1] = self._needle_color

        self._needle = vectorio.Polygon(
            points=[(100, 100), (100, 50), (50, 50), (50, 100)]
        )
        self._needle_vector_shape = vectorio.VectorShape(
            shape=self._needle,
            pixel_shader=self._needle_palette,
            x=0,
            y=0,
        )

        # if clipped, adjust the needle width up according to the clip amount
        if (
            (self._sweep_angle < 180)
            and (self._clip_needle)
            and (self._trim_line is not None)
        ):
            # calculate the line where the needle is most visible
            max_visible_angle = (2 * math.pi / 360) * (
                self._start_angle + self._sweep_angle / 2
            )
            while True:
                if max_visible_angle > math.pi:
                    max_visible_angle -= 2 * math.pi
                elif max_visible_angle < -math.pi:
                    max_visible_angle += 2 * math.pi
                else:
                    break

            temp_x = self._dial_center[0] + self._dial_radius * math.sin(
                max_visible_angle
            )
            temp_y = self._dial_center[1] - self._dial_radius * math.cos(
                max_visible_angle
            )

            temp_line = [self._dial_center, (temp_x, temp_y)]

            x, y = _line_intersection(temp_line, self._trim_line)

            needle_length_showing = math.sqrt((x - temp_x) ** 2 + (y - temp_y) ** 2)
            self._needle_width = round(
                self._needle_width_requested * self._dial_radius / needle_length_showing
            )
        else:
            self._needle_width = self._needle_width_requested

    def _update_value(self):

        if self._display_value:
            format_string = ("{" + self._value_format_string + "}").format(self._value)
            self._value_label.text = format_string

    def _update_position(self):
        if self._anchor_point is None or self._anchored_position is None:
            pass
        else:
            self.x = (
                -self._bounding_box[0]
                + self._anchored_position[0]
                - int(self._anchor_point[0] * self._bounding_box[2])
            )
            self.y = (
                -self._bounding_box[1]
                + self._anchored_position[1]
                - int(self._anchor_point[1] * self._bounding_box[3])
            )

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
        # A linear movement function (but can be modified with "easing functions"
        # for motion acceleration).

        # if multiple elements are present, they could each have their own movement functions.
        angle_offset = (2 * math.pi / 360) * (
            self._start_angle + self._sweep_angle * position
        )

        return angle_offset

    def _update_needle(self, value):
        if self._limit_rotation:  # constrain between min_value and max_value
            value = max(min(self._value, self._max_value), self._min_value)

        self._draw_position(
            value / (self._max_value - self._min_value)
        )  # convert to position (0.0 to 1.0)

    def _draw_position(self, position):
        # Draw the position of the needle.
        # The position parameter is a float between 0 and 1 (0= off, 1= on).

        # Get the position offset from the motion function
        angle_offset = self._get_offset_position(position)

        d_x = (self._needle_width / 2) * math.cos(angle_offset)
        d_y = (self._needle_width / 2) * math.sin(angle_offset)

        x_0 = round(self._dial_center[0] - d_x)
        y_0 = round(self._dial_center[1] - d_y)

        x_1 = round(self._dial_center[0] + d_x)
        y_1 = round(self._dial_center[1] + d_y)

        x_2 = round(self._dial_center[0] + self._dial_radius * math.sin(angle_offset))
        y_2 = round(self._dial_center[1] - self._dial_radius * math.cos(angle_offset))

        if (((2 * math.pi / 360) * self._sweep_angle) < math.pi) and self._clip_needle:
            # clip the needle points by adjusting (x0,y0) and (x1,y1)
            x_0, y_0 = _line_intersection(self._trim_line, [(x_0, y_0), (x_2, y_2)])
            x_1, y_1 = _line_intersection(self._trim_line, [(x_1, y_1), (x_2, y_2)])

            if (x_0 == x_1) and (y_0 == y_1):
                x_1 += 1
                y_1 += 1

        self._needle.points = [(x_0, y_0), (x_1, y_1), (x_2, y_2)]

    def resize(self, new_width, new_height):
        """Resizes the dial dimensions to the maximum size that will
        fit within the requested bounding box size (``new_width``, ``new_height``)

        :param int new_width: requested width, in pixels
        :param int new_height: requested height, in pixels
        """
        self._initialize_dial(new_width, new_height)

    @property
    def value(self):
        """The dial's value."""
        return self._value

    @value.setter
    def value(self, new_value):

        if new_value != self._value:
            self._value = new_value
            self._update_value()
            self._update_needle(self._value)

    @property
    def value_font(self):
        """The font used for the value's label."""
        return self._value_font

    @value_font.setter
    def value_font(self, new_font):
        if self._display_value:
            self._value_label.font = new_font
        self._value_font = new_font

    @property
    def value_color(self):
        """The font color used for the value's label."""
        return self._value_color

    @value_color.setter
    def value_color(self, new_color):
        if self._display_value:
            self._value_label.color = new_color
        self._value_color = new_color

    @property
    def dial_center(self):
        """The (x,y) pixel location of the dial's center of rotation."""
        return self._dial_center

    @property
    def dial_radius(self):
        """The length of the dial's radius, in pixels."""
        return self._dial_radius

    @property
    def start_angle(self):
        """The starting angle of the dial, in degrees."""
        return self._start_angle

    @property
    def sweep_angle(self):
        """The sweep angle of the dial, in degrees."""
        return self._sweep_angle


def draw_ticks(
    target_bitmap,
    *,
    dial_center,
    dial_radius,
    tick_count,
    tick_stroke,
    tick_length,
    start_angle,
    sweep_angle,
    tick_color_index=2,
):
    """Helper function for drawing ticks on the dial widget.  Can be used to
    customize the dial face.

    :param displayio.Bitmap target_bitmap: Bitmap where ticks will be drawn into
    :param (int,int) dial_center: the (x,y) pixel location in the bitmap of
     the dial's center of rotation
    :param int dial_radius: the radius of the dial (not including padding), in pixels
    :param int tick_count: number of ticks to be drawn
    :param int tick_stroke: the pixel width of the line used to draw the tick
    :param float start_angle: starting angle of the dial, in degrees
    :param float sweep_angle: total sweep angle of the dial, in degrees
    :param int tick_color_index: the bitmap's color index that should be used for
     drawing the tick marks
    """

    if tick_count <= 1:
        pass
    else:
        tick_bitmap = displayio.Bitmap(
            tick_stroke, tick_length, tick_color_index + 1
        )  # make a tick line bitmap for blitting
        tick_bitmap.fill(
            tick_color_index
        )  # initialize the tick bitmap with the tick_color_index

        for i in range(tick_count):
            this_angle = round(
                (start_angle + ((i * sweep_angle / (tick_count - 1))))
                * (2 * math.pi / 360),
                4,
            )  # in radians
            target_position_x = dial_center[0] + dial_radius * math.sin(this_angle)
            target_position_y = dial_center[1] - dial_radius * math.cos(this_angle)

            if "rotozoom" in dir(bitmaptools):  # if core function is available
                bitmaptools.rotozoom(
                    target_bitmap,
                    ox=round(target_position_x),
                    oy=round(target_position_y),
                    source_bitmap=tick_bitmap,
                    px=round(tick_bitmap.width / 2),
                    py=0,
                    angle=this_angle,  # in radians
                )

            else:
                _blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
                    destination=target_bitmap,
                    ox=target_position_x,
                    oy=target_position_y,
                    source=tick_bitmap,
                    px=int(tick_bitmap.width / 2),
                    py=0,
                    angle=this_angle,  # in radians
                )


def draw_labels(
    target_bitmap,
    *,
    font,
    font_height,
    tick_labels,
    dial_center,
    dial_radius,
    start_angle,
    sweep_angle,
    rotate_labels=True,
    tick_label_scale=1.0,
):
    """Helper function for drawing text labels on the dial widget.  Can be used
    to customize the dial face.

    :param displayio.Bitmap target_bitmap: Bitmap where ticks will be drawn into
    :param Font font: the font to be used to draw the tick mark text labels
    :param int font_height: the height of the font, used for text placement
    :param List[str] tick_labels: a list of strings for the tick text labels
    :param (int,int) dial_center: the (x,y) pixel location in the bitmap of
     the dial's center of rotation
    :param int dial_radius: the radius of the dial (not including padding), in pixels
    :param int tick_count: number of ticks to be drawn
    :param int tick_stroke: the pixel width of the line used to draw the tick
    :param float start_angle: starting angle of the dial, in degrees
    :param float sweep_angle: total sweep angle of the dial, in degrees
    :param bool rotate_labels: set to True if you want the label text to be rotated
     to align with the tick marks
    :param float tick_label_scale: scale factor for the tick text labels, default is 1.0
    """

    label_count = len(tick_labels)

    for i, this_label_text in enumerate(tick_labels):

        temp_label = bitmap_label.Label(
            font, text=this_label_text
        )  # make a tick line bitmap for blitting

        this_angle = (2 * math.pi / 360) * (
            start_angle + i * sweep_angle / (label_count - 1)
        )  # in radians

        target_position_x = dial_center[0] + (
            dial_radius + font_height // 2
        ) * math.sin(this_angle)
        target_position_y = dial_center[1] - (
            dial_radius + font_height // 2
        ) * math.cos(this_angle)

        if rotate_labels:
            pass
        else:
            this_angle = 0

        if "rotozoom" in dir(bitmaptools):  # if core function is available
            bitmaptools.rotozoom(
                target_bitmap,
                ox=round(target_position_x),
                oy=round(target_position_y),
                source_bitmap=temp_label.bitmap,
                px=round(temp_label.bitmap.width // 2),
                py=round(temp_label.bitmap.height // 2),
                angle=this_angle,
                scale=tick_label_scale,
            )

        else:
            _blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
                destination=target_bitmap,
                ox=round(target_position_x),
                oy=round(target_position_y),
                source=temp_label.bitmap,
                px=round(temp_label.bitmap.width // 2),
                py=round(temp_label.bitmap.height // 2),
                angle=this_angle,
                scale=tick_label_scale,
            )


# * Copyright (c) 2017 Werner Stoop <wstoop@gmail.com>
# *
# * Permission is hereby granted, free of charge, to any person obtaining a copy
# * of this software and associated documentation files (the "Software"), to deal
# * in the Software without restriction, including without limitation the rights
# * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# * copies of the Software, and to permit persons to whom the Software is
# * furnished to do so, subject to the following conditions:
# *
# * The above copyright notice and this permission notice shall be included in all
# * copies or substantial portions of the Software.
# *
# * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# * SOFTWARE.


# Credit from https://github.com/wernsey/bitmap
# MIT License from
#  * Copyright (c) 2017 Werner Stoop <wstoop@gmail.com>
#
# /**
# * #### `void bm_rotate_blit(Bitmap *dst, int ox, int oy, Bitmap *src, int px,
# * int py, double angle, double scale);`
# *
# * Rotates a source bitmap `src` around a pivot point `px,py` and blits it
# * onto a destination bitmap `dst`.
# *
# * The bitmap is positioned such that the point `px,py` on the source is at
# * the offset `ox,oy` on the destination.
# *
# * The `angle` is clockwise, in radians. The bitmap is also scaled by the
# * factor `scale`.
# */
# void bm_rotate_blit(Bitmap *dst, int ox, int oy, Bitmap *src, int px,
# int py, double angle, double scale);


#     /*
#    Reference:
#    "Fast Bitmap Rotation and Scaling" By Steven Mortimer, Dr Dobbs' Journal, July 01, 2001
#    http://www.drdobbs.com/architecture-and-design/fast-bitmap-rotation-and-scaling/184416337
#    See also http://www.efg2.com/Lab/ImageProcessing/RotateScanline.htm
#    */

# pylint: disable=invalid-name, too-many-branches, too-many-statements

# This function is provided in case the bitmaptools.rotozoom function is not available
def _blit_rotate_scale(
    destination,  # destination bitmap
    ox=None,
    oy=None,  # (ox, oy) is the destination point where the source (px,py) is placed
    dest_clip0=None,
    dest_clip1=None,  # clip0,1 is (x,y) corners of clip window on the destination bitmap
    source=None,  # source bitmap
    px=None,
    py=None,  # (px, py) is the rotation point of the source bitmap
    source_clip0=None,
    source_clip1=None,  # clip0,1 is (x,y) corners of clip window on the source bitmap
    angle=0,  # in radians, clockwise
    scale=1.0,  # scale factor (float)
    skip_index=None,  # color index to ignore
):

    if source is None:
        pass

    # Check the input limits

    if ox is None:
        ox = destination.width / 2
    if oy is None:
        oy = destination.height / 2
    if px is None:
        px = source.width / 2
    if py is None:
        py = source.height / 2

    if dest_clip0 is None:
        dest_clip0 = (0, 0)
    if dest_clip1 is None:
        dest_clip1 = (destination.width, destination.height)

    if source_clip0 is None:
        source_clip0 = (0, 0)
    if source_clip1 is None:
        source_clip1 = (source.width, source.height)

    minx = dest_clip1[0]
    miny = dest_clip1[1]
    maxx = dest_clip0[0]
    maxy = dest_clip0[1]

    sinAngle = math.sin(angle)
    cosAngle = math.cos(angle)

    dx = -cosAngle * px * scale + sinAngle * py * scale + ox
    dy = -sinAngle * px * scale - cosAngle * py * scale + oy
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(dy)
    dx = cosAngle * (source.width - px) * scale + sinAngle * py * scale + ox
    dy = sinAngle * (source.width - px) * scale - cosAngle * py * scale + oy
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(round(dy))

    dx = (
        cosAngle * (source.width - px) * scale
        - sinAngle * (source.height - py) * scale
        + ox
    )
    dy = (
        sinAngle * (source.width - px) * scale
        + cosAngle * (source.height - py) * scale
        + oy
    )
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(round(dy))

    dx = -cosAngle * px * scale - sinAngle * (source.height - py) * scale + ox
    dy = -sinAngle * px * scale + cosAngle * (source.height - py) * scale + oy
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(round(dy))

    # /* Clipping */
    if minx < dest_clip0[0]:
        minx = dest_clip0[0]
    if maxx > dest_clip1[0] - 1:
        maxx = dest_clip1[0] - 1
    if miny < dest_clip0[1]:
        miny = dest_clip0[1]
    if maxy > dest_clip1[1] - 1:
        maxy = dest_clip1[1] - 1

    dvCol = math.cos(angle) / scale
    duCol = math.sin(angle) / scale

    duRow = dvCol
    dvRow = -duCol

    startu = px - (ox * dvCol + oy * duCol)
    startv = py - (ox * dvRow + oy * duRow)

    rowu = startu + miny * duCol
    rowv = startv + miny * dvCol

    for y in range(miny, maxy + 1):  # (y = miny, y <= maxy, y++)
        u = rowu + minx * duRow
        v = rowv + minx * dvRow
        for x in range(minx, maxx + 1):  # (x = minx, x <= maxx, x++)
            if (source_clip0[0] <= u < source_clip1[0]) and (
                source_clip0[1] <= v < source_clip1[1]
            ):
                # get the pixel color (c) from the source bitmap at (u,v)
                c = source[
                    int(u) + source.width * int(v)
                ]  # direct index into bitmap is faster than tuple
                # c = source[int(u), int(v)]

                if c != skip_index:  # ignore any pixels with skip_index
                    # place the pixel color (c) into the destination bitmap at (x,y)
                    destination[
                        x + y * destination.width
                    ] = c  # direct index into bitmap is faster than tuple
                    # destination[x,y] = c
            u += duRow
            v += dvRow

        rowu += duCol
        rowv += dvCol


# Circle size calculations based on the angle intervals requested
# Algorithm source
# https://math.stackexchange.com/questions/45303/how-to-get-rectangular-size-of-arbitrary-circular-sector
def _isInInterval(theta, interval):
    theta = theta % 360
    i = interval[0] % 360
    f = interval[1] % 360
    if i < f:
        return (i <= theta <= f) and (theta <= f)
    return not f < theta < i


def _getXcoord(theta):
    return (1 + math.cos(theta * 2 * math.pi / 360)) / 2


def _getYcoord(theta):
    return (1 + math.sin(theta * 2 * math.pi / 360)) / 2


def _getCoords(interval, ignore_center=False):
    # This functions gets the maximum bounary dimensions of
    # a rectangle required to contain a partial circle with
    # the interval of (start_angle, end_angle)
    #
    # Parameter:
    #     interval = [start_angle, end_angle]
    #     ignore_center = Set True to exclude the centerpoint from the boundary
    #
    # Coordinates for calculations
    # 0 degrees is up
    # Circle diameter = 1.0
    # circle center is always at (0.5, 0.5)
    # upper left direction is (0.0, 0.0)
    # dimensions are in units of the circle's diameter (1.0 = diameter)
    #
    # Returns:
    #     (left, top, right, bottom, xCenter_offet, yCenter_offset)
    # coordinates of the minimum bounding box
    # and the xCenter_offset, yCenter_offset distance between
    # the upper left corner and the circle center

    i = interval[0]
    f = interval[1]

    xi = _getXcoord(i)
    yi = _getYcoord(i)
    xf = _getXcoord(f)
    yf = _getYcoord(f)

    is0 = _isInInterval(0, interval)
    is90 = _isInInterval(90, interval)
    is180 = _isInInterval(180, interval)
    is270 = _isInInterval(270, interval)

    if is0:
        top = 1.0
    else:
        if ignore_center:
            top = max(xi, xf)
        else:
            top = max(xi, xf, 0.5)

    if is90:
        right = 1.0
    else:
        if ignore_center:
            right = max(yi, yf)
        else:
            right = max(yi, yf, 0.5)

    if is180:
        bottom = 0
    else:
        if ignore_center:
            bottom = min(xi, xf)
        else:
            bottom = min(xi, xf, 0.5)

    if is270:
        left = 0
    else:
        if ignore_center:
            left = min(yi, yf)
        else:
            left = min(yi, yf, 0.5)

    xCenter_offset = 0.5 - left
    yCenter_offset = 0.5 - top

    # Correct coordinates so that upper left corner is (0,0)
    # Center is always at coordinate (0.5, 0.5)
    # All coordinates are in units of the circle's diameter
    # x,y Center_offset is the center point's offset relative to the upper left corner
    # (left, top, right, bottom, xCenter_offet, yCenter_offset)
    return [left, 1 - top, right, 1 - bottom, xCenter_offset, -yCenter_offset]


# Calculate the intersection point between two lines
# Source:
# https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines


def _line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def _det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = _det(xdiff, ydiff)
    if div == 0:
        raise Exception("lines do not intersect")

    d = (_det(*line1), _det(*line2))
    x = _det(d, xdiff) / div
    y = _det(d, ydiff) / div
    return round(x), round(y)
