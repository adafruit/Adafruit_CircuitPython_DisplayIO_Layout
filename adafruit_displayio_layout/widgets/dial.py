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

import gc
import math
import displayio
import vectorio
import bitmaptools

from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_text import bitmap_label
#from bitmap_scale_rotate import blit_rotate_scale

class Dial(Widget):
    """A dial widget.  The origin is set using ``x`` and ``y``.

    :param int x: pixel position
    :param int y: pixel position
    :param int width: width in pixels
    :param int height: height in pixels - is ignored
    :param int angle: dial rotation, in degrees, maximum value is 180 degrees.
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

    ..figure:: gui_layout_coordinates.png
      :scale: 50 %
      :alt: Diagram of layout coordinates

      Diagram showing the global and local coordinates and the associated
      class variables.
    """

    # The dial is a subclass of Group->Widget.

    def __init__(
        self,
        width=100,
        height=100,
        padding=0,  # keepout amount around border, in pixels
        sweep_angle=90, # maximum value is 180 degrees
        start_angle=None,
        clip_needle=False, # trims off the needle outside of the dial region, used for sweep_angles < 180
        needle_width=1,  # triangle with this base width at the radius center, best if this is odd
        needle_color=0x880000,
        value=0,
        value_font=None,
        display_value=True,
        value_color=0xFF0000,
        value_format_string=':0.0f',
        min_value=0.0,
        max_value=100.0,
        anchor_point=None,
        anchored_position=None,
        tick_color=0xFFFFFF,
        major_ticks=5, # if int, the total number of major ticks
        major_tick_stroke=3,
        major_tick_length=10,
        major_tick_labels=["0", "25", "50", "75", "100"],
        minor_ticks=5, # if int, the number of minor ticks per major tick
        minor_tick_stroke=1,
        minor_tick_length=5,
        tick_label_font=None,
        tick_label_color=0x880000,
        rotate_tick_labels=True,
        tick_label_scale=1.0,
        background_color=None,
        label_anchor_point=(0.5, -1.0),  # default label position uses (x-center point, y-text baseline)
        label_anchor_on_widget=(0.5, 0.5),  # default label position on widget
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

        self._value = value
        self._value_font = value_font
        self._value_color = value_color
        self._display_value = display_value
        self._value_format_string = value_format_string

        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        # validate sweep_angle and start_angle
        if sweep_angle > 360:
            raise ValueError("sweep_angle must be <= 360 degrees")

        sweep_angle = max(1, sweep_angle) # constrain to >= 1 to avoid divide by zero errors
        self._sweep_angle = sweep_angle

        if start_angle is None:
            start_angle = -sweep_angle / 2
        elif not (-360 <= start_angle <= 360):
            raise ValueError("start_angle must be between -360 and +360 degrees")
        self._start_angle = start_angle

        self._clip_needle = clip_needle
        self._needle_width_requested = needle_width
        self._needle_color = needle_color
        self._background_color = background_color

        self._min_value = min_value
        self._max_value = max_value

        self._major_tick_labels = major_tick_labels

        self._tick_color = tick_color
        self._tick_label_color = tick_label_color
        self._tick_label_font = tick_label_font
        self._tick_label_scale = tick_label_scale
        self._rotate_tick_labels = rotate_tick_labels

        self._major_ticks = major_ticks
        self._major_tick_stroke = major_tick_stroke
        self._major_tick_length = major_tick_length
        self._minor_ticks = minor_ticks
        self._minor_tick_stroke = minor_tick_stroke
        self._minor_tick_length = minor_tick_length

        self._label_anchor_point = label_anchor_point
        self._label_anchor_on_widget = label_anchor_on_widget

        self._padding = padding

        self._initialize_dial(width, height)

    def _initialize_dial(self, width, height):

        for i in range(len(self)):
            self.pop()

        # get the tick label font height
        self._font_height = self._get_font_height(font=self._tick_label_font, scale=self._tick_label_scale)

        self._adjust_dimensions(width, height)
        self._bounding_box = [0, 0, self._width, self._height]
        self._update_position()

        self._dial_palette = displayio.Palette(4)

        if (self._background_color is None):
            self._dial_palette.make_transparent(0)
            self._dial_palette[0] = 0x000000
        else:
            self._dial_palette[0] = self._background_color
        self._dial_palette[1] = self._tick_color
        self._dial_palette[2] = self._tick_label_color
        self._dial_bitmap = displayio.Bitmap(
            self._width, self._height, 3
        )  # 3 colors: background, ticks, tick label text
        self._dial_tilegrid = displayio.TileGrid(
            self._dial_bitmap, pixel_shader=self._dial_palette
        )

        self.append(self._dial_tilegrid)

        if self._display_value:
            self._value_label = (
                bitmap_label.Label(
                    self._value_font,
                    text=str(self._value),
                    color=self._value_color,
                    baseline_alignment=True,
                )
            )
            self._value_label.anchor_point = self._label_anchor_point
            self._value_label.anchored_position = [
                round(self._width * self._label_anchor_on_widget[0]),
                round(self._height * self._label_anchor_on_widget[1]),
            ]
            self.append(self._value_label)

            self._update_value()

        self._create_needle()

        self.append(self._needle_vector_shape)
        self._update_needle(self._value, initial_draw=True)

        _draw_ticks(
            target_bitmap=self._dial_bitmap,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            tick_count=self._major_ticks,
            tick_stroke=self._major_tick_stroke,
            tick_length=self._major_tick_length,
            start_angle=self._start_angle,
            sweep_angle=self._sweep_angle,
            tick_color_index=1,
        )

        _draw_ticks(
            target_bitmap=self._dial_bitmap,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            tick_count=self._minor_ticks * (self._major_ticks - 1) + 1,
            tick_stroke=self._minor_tick_stroke,
            tick_length=self._minor_tick_length,
            start_angle=self._start_angle,
            sweep_angle=self._sweep_angle,
            tick_color_index=1,
        )

        _draw_labels(
            target_bitmap=self._dial_bitmap,
            font=self._tick_label_font,
            tick_labels=self._major_tick_labels,
            dial_center=self._dial_center,
            dial_radius=self._dial_radius,
            start_angle=self._start_angle,
            sweep_angle=self._sweep_angle,
            rotate_labels=self._rotate_tick_labels,
            font_height=self._font_height,
            font_color_index=2,
            tick_label_scale=self._tick_label_scale,
        )



    def _adjust_dimensions(self, width, height):
        # get normalized dimensions of the dial based on start_angle and sweep_angle
        # in units of diameter

        # if the sweep angle is < 180, then adjust size if needle should clipped:
        if (self._sweep_angle < 180) and (self._clip_needle):
            [left, top, right, bottom, xCenter_calc, yCenter_calc] = _getCoords([self._start_angle, self._start_angle+self._sweep_angle], ignore_center=True)
        else:
            [left, top, right, bottom, xCenter_calc, yCenter_calc] = _getCoords([self._start_angle, self._start_angle+self._sweep_angle])

        # calculate the pixel dimension to fit within width/height (including padding)
        if (width-2*self._padding < 0) or (height-2*self._padding < 0):
            raise ValueError('Width, height, or padding size makes zero sized box')
        requested_aspect_ratio=(width-2*self._padding)/(height-2*self._padding)
        box_aspect_ratio = (right-left)/(bottom-top)

        if (box_aspect_ratio >= requested_aspect_ratio):
            # keep width and adjust the width
            self._width = width
            self._height = math.ceil( (width - 2 * self._padding) / box_aspect_ratio )  + (2 * self._padding)
            radius = round( (width - 2 * self._padding) / (2 * (right - left)) )

        else:
            # keep height and adjust the width
            self._height = height
            self._width = math.ceil( ((height - 2 * self._padding) * box_aspect_ratio) ) + (2 * self._padding)
            radius = round( (height - 2 * self._padding) / (2 * (bottom-top)) )

        centerX = round(xCenter_calc*radius*2) + self._padding
        centerY = round(yCenter_calc*radius*2) + self._padding
        self._dial_center = (centerX, centerY)
        self._dial_radius = radius

        if self._clip_needle: # define the line endpoints that will trim off the needle
            trim_x1 = round(centerX + math.sin(self._start_angle *2*math.pi/360) * (self._dial_radius - self._padding))
            trim_y1 = round(centerY - math.cos(self._start_angle *2*math.pi/360) * (self._dial_radius - self._padding))
            trim_x2 = round(centerX + math.sin( (self._start_angle+self._sweep_angle) *2*math.pi/360) * (self._dial_radius - self._padding))
            trim_y2 = round(centerY - math.cos( (self._start_angle+self._sweep_angle) *2*math.pi/360) * (self._dial_radius - self._padding))
            self._trim_line = [ (trim_x1, trim_y1), (trim_x2, trim_y2) ]
        else:
            self._trim_line = None

    def _get_font_height(self, font, scale):
        if (self._major_tick_labels == []) or (font is None):
            font_height = 0
        else:
            if hasattr(font, "get_bounding_box"):
                font_height = int(
                    scale * font.get_bounding_box()[1]
                )
            elif hasattr(font, "ascent"):
                font_height = int(
                    scale * font.ascent + font.ascent
                )
        return font_height

    def _create_needle(self):
        # Create the needle
        self._needle_palette = displayio.Palette(2)
        self._needle_palette.make_transparent(0)
        self._needle_palette[1] = self._needle_color

        self._needle=vectorio.Polygon(points=[ (100,100), (100,50), (50,50), (50,100) ])
        self._needle_vector_shape = vectorio.VectorShape(shape=self._needle,
                                                         pixel_shader=self._needle_palette,
                                                         x=0, y=0,
                                                         )

        # if clipped, adjust the needle width up according to the clip amount
        if (self._sweep_angle < 180) and (self._clip_needle) and (self._trim_line is not None):
            # calculate the line where the needle is most visible
            max_visible_angle = (2*math.pi/360) * (self._start_angle + self._sweep_angle/2)
            while True:
                if max_visible_angle > math.pi:
                    max_visible_angle -= 2*math.pi
                elif max_visible_angle < -math.pi:
                    max_visible_angle += 2*math.pi
                else:
                    break

            print("max_visible_angle: {}".format(max_visible_angle * 360 / (2*math.pi)))

            temp_x = self._dial_center[0] + self._dial_radius * math.sin(max_visible_angle)
            temp_y = self._dial_center[1] - self._dial_radius * math.cos(max_visible_angle)

            temp_line = [self._dial_center, (temp_x, temp_y)]

            x,y = _line_intersection(temp_line, self._trim_line)

            needle_length_showing = math.sqrt( (x-temp_x)**2 + (y-temp_y)**2 )
            self._needle_width = round(self._needle_width_requested * self._dial_radius/needle_length_showing)

    def _update_value(self):

        if self._display_value:
            format_string = ('{'+self._value_format_string+'}').format(self._value)
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
        # A linear movement function (but can be modified for other motion acceleration)
        if position < 0:
            position = 0
        if position > 1:
            position = 1

        # if multiple elements are present, they could each have their own movement functions.
        angle_offset = (2*math.pi/360) * (self._start_angle + self._sweep_angle * position)

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

        dx= self._needle_width/2 * math.cos(angle_offset)
        dy= self._needle_width/2 * math.sin(angle_offset)

        x0=round( self._dial_center[0] - dx )
        y0=round( self._dial_center[1] - dy )

        x1=round( self._dial_center[0] + dx )
        y1=round( self._dial_center[1] + dy )

        x2=round( self._dial_center[0] + self._dial_radius * math.sin(angle_offset) )
        y2=round( self._dial_center[1] - self._dial_radius * math.cos(angle_offset) )

        if ( (((2*math.pi/360) * self._sweep_angle ) < math.pi) and self._clip_needle ):
            # clip the needle points by adjusting (x0,y0) and (x1,y1)
            x0, y0 = _line_intersection( self._trim_line, [(x0, y0), (x2, y2)] )
            x1, y1 = _line_intersection( self._trim_line, [(x1, y1), (x2, y2)] )

            if (x0==x1) and (y0==y1):
                x1+=1
                y1+=1

        self._needle.points=[ (x0,y0), (x1,y1), (x2,y2) ]

    def resize(self, new_width, new_height):
        self._initialize_dial(new_width, new_height)

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

    @property
    def value_font(self):
        return self._value_font

    @value_font.setter
    def value_font(self, new_font):
        if self._display_value:
            self._value_label.font=new_font
        self._value_font=new_font

    @property
    def value_color(self):
        return self._value_color

    @value_font.setter
    def value_color(self, new_color):
        if self._display_value:
            self._value_label.color=new_color
        self._value_color=new_color

def _draw_ticks(
    target_bitmap,
    *,
    dial_center,
    dial_radius,
    tick_count,
    tick_stroke,
    tick_length,
    start_angle,
    sweep_angle,
    tick_color_index,
):
    # angle is in degrees

    if tick_count <= 1:
        pass
    else:
        tick_bitmap = displayio.Bitmap(
            tick_stroke, tick_length, 2
        )  # make a tick line bitmap for blitting
        tick_bitmap.fill(
            tick_color_index
        )  # initialize the tick bitmap with the tick_color_index

        # print("dial_radius: {}".format(dial_radius))
        # print("bitmap width: {} height: {}".format(target_bitmap.width, target_bitmap.height))
        for i in range(tick_count):
            this_angle = round((start_angle + ( (i * sweep_angle / (tick_count - 1)) )) * (2 * math.pi / 360), 4) # in radians
            target_position_x = dial_center[0] + dial_radius * math.sin(this_angle)
            target_position_y = dial_center[1] - dial_radius * math.cos(this_angle)
            #print('this_angle: {}, i: {}, tick_count: {}'.format(this_angle*180/math.pi, i, tick_count))

            # print("target position x,y: {},{}".format(target_position_x, target_position_y))

            if "rotozoom" in dir(bitmaptools):  # if core function is available
                bitmaptools.rotozoom(target_bitmap,
                    ox=round(target_position_x),
                    oy=round(target_position_y),
                    source_bitmap=tick_bitmap,
                    px=round(tick_bitmap.width / 2),
                    py=0,
                    angle=this_angle, # in radians
                )

            else:
                blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
                    destination=target_bitmap,
                    ox=target_position_x,
                    oy=target_position_y,
                    source=tick_bitmap,
                    px=int(tick_bitmap.width / 2),
                    py=0,
                    angle=this_angle, # in radians
                )


def _draw_labels(
    target_bitmap,
    *,
    font,
    tick_labels,
    dial_center,
    dial_radius,
    start_angle,
    sweep_angle,
    font_height,
    font_color_index=2,
    rotate_labels=True,
    tick_label_scale,
):
    # input angles are in degrees

    label_count = len(tick_labels)

    for i, this_label_text in enumerate(tick_labels):

        temp_label = bitmap_label.Label(
            font, text=this_label_text
        )  # make a tick line bitmap for blitting
        # may need to convert color

        this_angle = (2*math.pi/360) * (start_angle + i * sweep_angle / (
            label_count - 1
        ) ) # in radians

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


        if "rotozoom" in dir(bitmaptools):  # if core function is available
            bitmaptools.rotozoom(target_bitmap,
                ox=round(target_position_x),
                oy=round(target_position_y),
                source_bitmap=temp_label.bitmap,
                px=round(temp_label.bitmap.width  // 2),
                py=round(temp_label.bitmap.height // 2),
                angle=this_angle,
                scale=tick_label_scale,
            )

        else:
            blit_rotate_scale(  # translate and rotate the tick into the target_bitmap
                destination=target_bitmap,
                ox=round(target_position_x),
                oy=round(target_position_y),
                source=temp_label.bitmap,
                px=round(temp_label.bitmap.width  // 2),
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


# Circle size calculations based on the angle intervals requested
# Algorithm source
# https://math.stackexchange.com/questions/45303/how-to-get-rectangular-size-of-arbitrary-circular-sector

def _isInInterval(theta, interval):
    theta = theta % 360
    i = interval[0] % 360
    f = interval[1] % 360
    if (i < f):
        return ( (theta >= i) and (theta <= f) )
    else:
        return (not ( (theta < i) and (theta > f) ) )

def _getXcoord(theta):
    return ( (1+math.cos(theta * 2 * math.pi / 360))/2 )

def _getYcoord(theta):
    return ( (1+math.sin(theta * 2 * math.pi / 360))/2 )

def _getCoords(interval, ignore_center=False):
    # This functions gets the maximum dimensions of
    # a rectangle required to contain a partial circle with
    # the interval of (start_angle, end_angle)
    #
    # Parameter:
    #     interval = [start_angle, end_angle]
    #
    # Coordinates for calculations
    # 0 degrees is up
    # Circle diameter = 1.0
    # circle center is always at (0.5, 0.5)
    # upper left direction is (0.0, 0.0)
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

    is0   = _isInInterval(0,   interval)
    is90  = _isInInterval(90,  interval)
    is180 = _isInInterval(180, interval)
    is270 = _isInInterval(270, interval)

    if is0:
        top = 1.0
        top_raw = top
    else:
        if ignore_center:
            top = max(xi, xf)
        else:
            top = max(xi, xf, 0.5)
        top_raw = max(xi, xf, 0.5)

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
        left_raw = left
    else:
        if ignore_center:
            left = min(yi, yf)
        else:
            left = min(yi, yf, 0.5)
        left_raw = min(yi, yf, 0.5)

    xCenter_offset = 0.5 - left
    yCenter_offset = 0.5 - top

    # Correct coordinates so that upper left corner is (0,0)
    # Center is always at coordinate (0.5, 0.5)
    # All coordinates are in units of the circle's diameter
    # x,y Center_offset is the center point's offset relative to the upper left corner

    # (left, top, right, bottom, xCenter_offet, yCenter_offset)
    return [left, 1-top, right, 1-bottom, xCenter_offset, -yCenter_offset]


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
       raise Exception('lines do not intersect')

    d = (_det(*line1), _det(*line2))
    x = _det(d, xdiff) / div
    y = _det(d, ydiff) / div
    return round(x), round(y)


