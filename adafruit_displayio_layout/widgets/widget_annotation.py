# The MIT License (MIT)
#
# Copyright (c) 2021 Kevin Matocha <ksmatocha@gmail.com>
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
#

import time
import displayio

from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_display_shapes.line import Line
from adafruit_display_text import bitmap_label


class WidgetAnnotation(Widget):
    """A widget to be used to annotate other widgets with text and lines.
    :param Widget widget: the widget to be annotated, all dimensions are relative to
      this widget.  The annotation position on the widget can be defined by either
      the `anchor_point` (in relative dimensions of the size of the widget)
      or the `anchored_position` (in raw pixel dimensions relative to the origin
      of the widget).
    :param str text: text to be displayed in the annotation.
    :param Font font: font to be used for the text.
    :param anchor_point: starting point for the annotation line, where `anchor_point` is an
      (A,B) tuple in relative units of the size of the widget,
      for example (0.0, 0.0) is the upper left corner, and (1.0, 1.0) is the lower
      right corner of the widget.  If `anchor_point` is `None`, then `anchored_position`
      is used to set the annotation line starting point (in widget size relative units).
    :type anchor_point: Tuple[float, float]
    :param anchored_position: starting point for the annotation line where
      `anchored_position` is an (x,y) tuple in pixel units relative to the
      upper left corner of the widget. (in pixel units)
    :type anchored_position: Tuple[int, int]
    :param position_offset: an (x,y) pixel offset added to the annotation line starting
      point, either set by `anchor_point` or `anchored_position` (in pixel units).
    :type position_offset: Tuple[int, int]
    :param int delta_x: the x-offset for the second end of the line where the text
      will reside (in pixel units).
    :param int delta_y: the y-offset for the second end of the line where the text
      will reside (in pixel units).
    :param int stroke: the annotation line width (in pixels). [NOT currently implemented]
    :param int line_color: the color of the annotation line (in RGB 0xFFFFFF values).
    :param int text_color: the color of the text, if set to `None` color will be
      set to `line_color` (in RGB 0xFFFFFF values).
    :param text_offset: a (x,y) pixel offset to adjust text position relative
      to annotation line (in pixel units).
    :type text_offset: Tuple[int, int]
    :param Boolean text_under: set `True` for text to be placed below the
      annotation line.
    """

    def __init__(
        self,
        widget,  # widget for placement
        text=None,
        font=None,
        delta_x=-15,  # line dimension, x-distance
        delta_y=-10,  # line dimension, y-distance
        anchor_point=None,  # Choose anchor_point (A,B) or anchored_position (x,y), relative to widget dimensions
        anchored_position=None,
        position_offset=(0, 0),  # Add a pixel offset to line point 0
        stroke=1,  # line width, not currently implemented in adafruit_display_shapes/line.py
        line_color=0xFFFFFF,  # line color
        text_color=None,  # text color
        text_offset=(0, -1),  # move text by this many pixels
        text_under=False,  # set True to put text underneath
    ):

        if font is None:  # use the default built in font
            import terminalio

            font = terminalio.FONT

        widget_width = widget.bounding_box[2]
        widget_height = widget.bounding_box[3]
        if anchor_point is not None:
            line_x0 = (
                widget.x + round(widget_width * anchor_point[0]) + position_offset[0]
            )
            line_y0 = (
                widget.y + round(widget_height * anchor_point[1]) + position_offset[1]
            )
        elif anchored_position is not None:
            line_x0 = widget.x + anchored_position[0] + position_offset[0]
            line_y0 = widget.y + anchored_position[1] + position_offset[1]
        else:
            raise ValueError("Must supply either anchor_point or anchored_position")

        line_x1 = line_x0 + delta_x
        line_y1 = line_y0 + delta_y

        text_anchor_point = (0.0, 1.0)  # bottom left corner
        underline_x_multiplier = 1

        if delta_x < 0:
            text_anchor_point = (1.0, 1.0)  # set to right corner
            underline_x_multiplier = -1

        if (
            text_under
        ):  # if text is under the line, set to text_anchor_point to upper edge
            text_anchor_point = (text_anchor_point[0], 0.0)

        if text_color is None:
            text_color = line_color

        self._label = bitmap_label.Label(
            text=text,
            font=font,
            color=text_color,
            anchor_point=text_anchor_point,
            anchored_position=(line_x1 + text_offset[0], line_y1 + text_offset[1]),
        )

        label_width = self._label.bounding_box[2]
        line_x2 = line_x1 + label_width * underline_x_multiplier + text_offset[0]
        # lengthen the line if the text is offset
        line_y2 = line_y1

        self._line0 = Line(line_x0, line_y0, line_x1, line_y1, color=line_color)
        self._line1 = Line(line_x1, line_y1, line_x2, line_y2, color=line_color)

        super().__init__(max_size=3)
        # Group elements:
        # 0. Line0
        # 1. Line1
        # 2. Label

        self.append(self._line0)
        self.append(self._line1)
        self.append(self._label)
