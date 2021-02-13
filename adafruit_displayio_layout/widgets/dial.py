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

import gc

#import time
import terminalio
import math
import displayio

from adafruit_displayio_layout.widgets.widget import Widget

from adafruit_display_shapes.line import Line
from adafruit_display_shapes.triangle import Triangle

from adafruit_display_text import bitmap_label
#from adafruit_display_text import label

from bitmap_scale_rotate import blit_rotate_scale


class Dial(Widget):
    """A dial widget.  The origin is set using ``x`` and ``y``.

    :param int x: pixel position
    :param int y: pixel position
    :param int width: width in pixels
    :param int height: height in pixels - is ignored
    :param int angle: dial rotation, in degrees
    :param float value: the value to display
    :param Boolean display_value: show the value on the dial
    :param float min_value: the minimum value on the dial
    :param float max_value: the maximum value on the dial
    :param float anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor
     point relative to the bounding box
    :param int anchored_position: (x,y) pixel value for the location
     of the anchor_point

    :param tick_color: tick line color (RGB tuple or 24-bit hex value)

    :param int major_ticks: number of major ticks
    :param int major_tick_stroke: major tick line width, in pixels
    :param int major_tick_length: major tick length, in pixels
    :param str major_tick_labels: array of strings for major tick labels
    :param tick_label_font: font to be used for tick label
    :param tick_label_color: color for the tick labels
    :param Boolean angle_tick_labels: Set True if the tick_labels should be angled

    :param int minor_ticks: number of minor ticks (per major tick)
    :param int minor_tick_stroke: minor tick line width, in pixels
    :param int minor_tick_length: minor tick length, in pixels


    :param background_color: background color (RGB tuple
     or 24-bit hex value), set None for transparent
    """
    # ***** Add label_anchor_point and label_anchor_on_widget (rename?????) *****

    # This Switch has multiple class inheritances.
    # It is a subclass of Group->Widget and a sublcass of Control.

    # *** Update to handle angles > 180 degrees

    def __init__(
        self,
        width=100,
        padding=0,  # keepout amount around border, in pixels
        sweep_angle=90,
        start_angle=None,
        needle_width=1,  # triangle with this base width at the radius center, best if this is odd
        needle_color=0x880000,
        value=0,
        value_font=None,
        display_value=True,
        value_color=0xFF0000,
        min_value=0.0,
        max_value=100.0,
        anchor_point=None,
        anchored_position=None,
        tick_color=0xFFFFFF,
        major_ticks=5,
        major_tick_stroke=3,
        major_tick_length=10,
        major_tick_labels=["0", "25", "50", "75", "100"],
        minor_ticks=5,
        minor_tick_stroke=1,
        minor_tick_length=5,
        tick_label_font=terminalio.FONT,
        tick_label_color=0x880000,
        rotate_tick_labels=True,
        tick_label_scale=1.0,
        background_color=None,
        label_anchor_point=(0.5, 0.5),  # default label position
        label_anchor_on_widget=(0.5, 0.5),  # default label position on widget
        **kwargs,
    ):

        # initialize the Widget superclass (x, y, scale)
        super().__init__(**kwargs, max_size=3)
        # Define how many graphical elements will be in this group
        # using "max_size=XX"
        #
        # Group elements for SwitchRoundHorizontal:
        #  1. TileGrid holding bitmap with ticks and tick label text
        #  2. Value label (optional)
        #  3. Needle bitmap

        self._value = value
        if value_font is None:
            self.value_font = terminalio.FONT
        else:
            self.value_font = value_font

        self._value_color = value_color
        self._display_value = display_value

        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        sweep_angle = min(max(1, sweep_angle), 180)
        # print("sweep_angle: {}".format(sweep_angle))
        self._sweep_angle_radians = (sweep_angle * 2 * math.pi) / 360
        if start_angle is None:
            start_angle = -sweep_angle / 2
        self._start_angle_radians = 2 * math.pi * start_angle / 360
        # ***** Updated dial code to handle different starting angle

        self._min_value = min_value
        self._max_value = max_value

        if (major_tick_labels == []) or (tick_label_font is None):
            font_height = 0
        else:
            if hasattr(tick_label_font, "get_bounding_box"):
                font_height = int(
                    tick_label_scale * tick_label_font.get_bounding_box()[1]
                )
            elif hasattr(font, "ascent"):
                font_height = int(
                    tick_label_scale * tick_label_font.ascent + tick_label_font.ascent
                )

        self._dial_radius = (width / 2 - font_height - padding) / math.sin(
            self._sweep_angle_radians / 2
        )
        # print("dial_radius: {}".format(self._dial_radius))
        self._width = width
        # print("calc height: {}".format(int( self._dial_radius - (self._dial_radius - major_tick_length) * math.cos(self._sweep_angle_radians/2) )))
        self._height = (
            2 * padding
            + int(
                font_height
                + self._dial_radius
                - (self._dial_radius - major_tick_length)
                * math.cos(self._sweep_angle_radians / 2)
            )
            + major_tick_stroke
        )
        # print("self._height: {}".format(self._height))

        self._padding = padding

        self._dial_center = (
            int(width / 2),
            int(self._dial_radius) + font_height + padding,
        )

        self._dial_palette = displayio.Palette(4)
        self._dial_palette.make_transparent(
            0
        )  # comment this out for debug of bitmap bounding box
        self._dial_palette[0] = 0x333333
        self._dial_palette[1] = tick_color
        self._dial_palette[2] = tick_label_color
        self._dial_bitmap = displayio.Bitmap(
            self._width, self._height, 3
        )  # 3 colors: background, ticks, tick label text
        self._dial_tilegrid = displayio.TileGrid(
            self._dial_bitmap, pixel_shader=self._dial_palette
        )

        self.append(self._dial_tilegrid)

        if self._display_value:
            self._value_label = (
                bitmap_label.Label(  # label runs faster than bitmap_label
                    self.value_font,
                    text=str(self._value),
                    color=self._value_color,
                )
            )
            self._value_label.anchor_point = label_anchor_point

            self._value_label.anchored_position = [
                round(self._width * label_anchor_on_widget[0]),
                round(self._height * label_anchor_on_widget[1]),
            ]

            self.append(self._value_label)

            self._update_value()

        self._needle_palette = displayio.Palette(4)
        self._needle_palette.make_transparent(0)
        self._needle_palette[1] = needle_color
        self._needle_palette[2] = needle_color
        self._needle_bitmap = displayio.Bitmap(
            self._width, self._height, 4
        )  # 2 colors: clear and needle_color
        self._needle_tilegrid = displayio.TileGrid(
            self._needle_bitmap, pixel_shader=self._needle_palette
        )
        self._needle_width = needle_width
        self._needle_color = needle_color

        # self._needle_origin = Triangle(
        #                             x0=0,
        #                             y0=0,
        #                             x1=int(round(needle_width/2)),
        #                             y1=int(self._dial_radius),
        #                             x2=-int(round(needle_width/2)),
        #                             y2=int(self._dial_radius),
        #                             fill=needle_color,
        #                             outline=needle_color,
        #                             )

        # self.append(self._needle_origin)

        self._update_needle(self._value, initial_draw=True)

        draw_ticks(
            target_bitmap=self._dial_bitmap,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            tick_count=major_ticks,
            tick_stroke=major_tick_stroke,
            tick_length=major_tick_length,
            angle=sweep_angle,
            tick_color_index=1,
        )

        draw_ticks(
            target_bitmap=self._dial_bitmap,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            tick_count=minor_ticks * (major_ticks - 1) + 1,
            tick_stroke=minor_tick_stroke,
            tick_length=minor_tick_length,
            angle=sweep_angle,
            tick_color_index=1,
        )

        draw_labels(
            target_bitmap=self._dial_bitmap,
            font=tick_label_font,
            tick_labels=major_tick_labels,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            start_angle_radians=self._start_angle_radians,
            sweep_angle_radians=self._sweep_angle_radians,
            rotate_labels=rotate_tick_labels,
            font_height=font_height,
            font_color_index=2,
            tick_label_scale=tick_label_scale,
        )

        self._bounding_box = [0, 0, self._width, self._height]

        # update the position, if required
        self._update_position()

    def _update_value(self):

        if self._display_value:
            self._value_label.text = str(self._value)

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
        # A linear movement function (but can be modified for other motion acceleration)
        if position < 0:
            position = 0
        if position > 1:
            position = 1

        # if multiple elements are present, they could each have their own movement functions.
        angle_offset = self._start_angle_radians + self._sweep_angle_radians * position

        return angle_offset

    def _update_needle(self, value, initial_draw=False):
        self._draw_position(
            value / (self._max_value - self._min_value), initial_draw=initial_draw
        )  # convert to position (0.0 to 1.0)

    def _draw_position(self, position, initial_draw=False):
        # Draw the position of the slider.
        # The position parameter is a float between 0 and 1 (0= off, 1= on).

        # Get the position offset from the motion function
        angle_offset = self._get_offset_position(position)
        # print("angle_offset: {}".format(angle_offset))

        if self._sweep_angle_radians > 0.95 * math.pi:
            self._needle_origin = Triangle(
                x0=round(self._dial_radius * math.sin(angle_offset)),
                y0=round(-self._dial_radius * math.cos(angle_offset)),
                x1=round(-self._needle_width / 2 * math.cos(angle_offset)),
                y1=round(-self._needle_width / 2 * math.sin(angle_offset)),
                x2=round(self._needle_width / 2 * math.cos(angle_offset)),
                y2=round(self._needle_width / 2 * math.sin(angle_offset)),
                fill=self._needle_color,
                outline=self._needle_color,
            )
            if angle_offset > 0:
                self._needle_origin.x = self._dial_center[0] - round(
                    self._needle_width / 2 * math.cos(angle_offset)
                )
                self._needle_origin.y = (
                    self._dial_center[1]
                    - self._needle_origin._bitmap.height
                    + round(self._needle_width / 2 * math.sin(angle_offset))
                )
            elif angle_offset < 0:
                self._needle_origin.x = (
                    self._dial_center[0]
                    - self._needle_origin._bitmap.width
                    + round(self._needle_width / 2 * math.cos(angle_offset))
                )
                self._needle_origin.y = (
                    self._dial_center[1]
                    - self._needle_origin._bitmap.height
                    - round(self._needle_width / 2 * math.sin(angle_offset))
                )
            else:
                self._needle_origin.x = (
                    self._dial_center[0] - self._needle_origin._bitmap.width // 2
                )
                self._needle_origin.y = (
                    self._dial_center[1] - self._needle_origin._bitmap.height
                )

        else:

            # x,y position of tip of needle
            needle_x = self._dial_center[0] + round(
                self._dial_radius * math.sin(angle_offset)
            )
            needle_y = self._dial_center[1] - round(
                self._dial_radius * math.cos(angle_offset)
            )

            x0 = round(self._dial_radius * math.sin(angle_offset))
            y0 = round(-self._dial_radius * math.cos(angle_offset))
            x1_start = round(-self._needle_width / 2 * math.cos(angle_offset))
            y1_start = round(-self._needle_width / 2 * math.sin(angle_offset))
            x2_start = round(self._needle_width / 2 * math.cos(angle_offset))
            y2_start = round(self._needle_width / 2 * math.sin(angle_offset))

            # y_prime: how much of the needle should be showing
            y_prime = self._dial_bitmap.height - needle_y  # -self._padding
            x1_prime = (x1_start - x0) * (y_prime / (y1_start - y0))
            x2_prime = (x2_start - x0) * (y_prime / (y2_start - y0))

            if y1_start - y0 < y_prime:
                x1_needle = x1_start
                y1_needle = y1_start
            else:
                x1_needle = x0 + x1_prime
                y1_needle = y0 + y_prime

            if y2_start - y0 < y_prime:
                x2_needle = x2_start
                y2_needle = y2_start
            else:
                x2_needle = x0 + x2_prime
                y2_needle = y0 + y_prime

            self._needle_origin = Triangle(
                x0=x0,
                y0=y0,
                x1=int(x1_needle),
                y1=int(y1_needle),
                x2=int(x2_needle),
                y2=int(y2_needle),
                fill=self._needle_color,
                outline=self._needle_color,
            )
            gc.collect()

            if angle_offset < 0:
                self._needle_origin.x = needle_x - int(
                    max(0, x0 - x1_needle)
                )  # offset for partially angled needle
                self._needle_origin.y = needle_y
            elif angle_offset > 0:
                self._needle_origin.x = (
                    needle_x
                    - self._needle_origin._bitmap.width
                    + int(max(0, x2_needle - x0))
                )  # offset for partially angled needle
                self._needle_origin.y = needle_y
            else:
                self._needle_origin.x = round(
                    self._dial_center[0] - self._needle_origin._bitmap.width / 2
                )
                self._needle_origin.y = round(self._dial_center[1] - self._dial_radius)

        if initial_draw:
            self.append(self._needle_origin)
        else:
            self[len(self) - 1] = self._needle_origin

    @property
    def value(self):
        """The current switch value (Boolean)."""
        return self._value

    @value.setter
    def value(self, new_value):

        if new_value != self._value:
            self._value = new_value
            self._update_value()
            self._update_needle(self._value)


def draw_ticks(
    target_bitmap,
    *,
    dial_center,
    dial_radius,
    tick_count,
    tick_stroke,
    tick_length,
    angle,
    tick_color_index,
):
    # angle is in degrees

    tick_bitmap = displayio.Bitmap(
        tick_stroke, tick_length, 2
    )  # make a tick line bitmap for blitting
    tick_bitmap.fill(
        tick_color_index
    )  # initialize the tick bitmap with the tick_color_index

    # print("dial_radius: {}".format(dial_radius))
    # print("bitmap width: {} height: {}".format(target_bitmap.width, target_bitmap.height))
    for i in range(tick_count):
        this_angle = (
            (-(angle / 2) + i * angle / (tick_count - 1)) * 2 * math.pi / 360
        )  # in radians

        target_position_x = dial_center[0] + dial_radius * math.sin(this_angle)
        target_position_y = dial_center[1] - dial_radius * math.cos(this_angle)

        # print("target position x,y: {},{}".format(target_position_x, target_position_y))

        if "fancyblit" in dir(displayio.Bitmap):  # if core function is available
            target_bitmap.fancyblit(
                ox=target_position_x,
                oy=target_position_y,
                source_bitmap=tick_bitmap,
                px=int(tick_bitmap.width / 2),
                py=0,
                angle=this_angle,
            )

        else:
            blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
                destination=target_bitmap,
                ox=target_position_x,
                oy=target_position_y,
                source=tick_bitmap,
                px=int(tick_bitmap.width / 2),
                py=0,
                angle=this_angle,
            )


def draw_labels(
    target_bitmap,
    *,
    font,
    tick_labels,
    dial_center,
    dial_radius,
    start_angle_radians,
    sweep_angle_radians,
    font_height,
    font_color_index=2,
    rotate_labels=True,
    tick_label_scale,
):

    label_count = len(tick_labels)

    for i, this_label_text in enumerate(tick_labels):

        temp_label = bitmap_label.Label(
            font, text=this_label_text
        )  # make a tick line bitmap for blitting
        # may need to convert color

        this_angle = start_angle_radians + i * sweep_angle_radians / (
            label_count - 1
        )  # in radians

        target_position_x = dial_center[0] + (
            dial_radius + font_height // 2
        ) * math.sin(this_angle)
        target_position_y = dial_center[1] - (
            dial_radius + font_height // 2
        ) * math.cos(this_angle)

        # print("target position x,y: {},{}".format(target_position_x, target_position_y))

        if rotate_labels:
            pass
        else:
            this_angle = 0
        blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
            destination=target_bitmap,
            ox=target_position_x,
            oy=target_position_y,
            source=temp_label.bitmap,
            px=temp_label.bitmap.width // 2,
            py=temp_label.bitmap.height // 2,
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
# * #### `void bm_rotate_blit(Bitmap *dst, int ox, int oy, Bitmap *src, int px, int py, double angle, double scale);`
# *
# * Rotates a source bitmap `src` around a pivot point `px,py` and blits it onto a destination bitmap `dst`.
# *
# * The bitmap is positioned such that the point `px,py` on the source is at the offset `ox,oy` on the destination.
# *
# * The `angle` is clockwise, in radians. The bitmap is also scaled by the factor `scale`.
# */
# void bm_rotate_blit(Bitmap *dst, int ox, int oy, Bitmap *src, int px, int py, double angle, double scale);


#     /*
#    Reference:
#    "Fast Bitmap Rotation and Scaling" By Steven Mortimer, Dr Dobbs' Journal, July 01, 2001
#    http://www.drdobbs.com/architecture-and-design/fast-bitmap-rotation-and-scaling/184416337
#    See also http://www.efg2.com/Lab/ImageProcessing/RotateScanline.htm
#    */

import math

def blit_rotate_scale(
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

