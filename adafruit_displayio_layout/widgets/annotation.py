# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
"""

`annotation`
================================================================================
A widget for annotating other widgets or freeform positions.

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# pylint: disable=too-many-arguments, too-many-locals, unused-argument

from terminalio import FONT
from adafruit_display_text import bitmap_label
from adafruit_display_shapes.line import Line
from adafruit_displayio_layout.widgets.widget import Widget


class Annotation(Widget):
    """A widget to be used to annotate other widgets with text and lines, but can also
     be used freeform by using ``(x,y)`` parameter.

    :param int x: x-direction pixel position for the end of the annotation line for
     freeform positioning, ``(x,y)`` will be ignored if a ``widget`` and ``anchor_point`` and/or
     ``anchored_position`` are provided.
    :param int y: y-direction pixel position for the end of the annotation line for
     freeform positioning.

    :param Widget widget: the widget to be annotated, all dimensions are relative to
      this widget.  The annotation line position will be defined by either
      the ``anchor_point`` (in relative dimensions of the size of the widget)
      or the ``anchored_position`` (in raw pixel dimensions relative to the origin
      of the widget).

    :param str text: text to be displayed in the annotation.
    :param Font font: font to be used for the text.

    :param anchor_point: starting point for the annotation line, where ``anchor_point`` is an
      (A,B) tuple in relative units of the size of the widget,
      for example (0.0, 0.0) is the upper left corner, and (1.0, 1.0) is the lower
      right corner of the widget.  If ``anchor_point`` is `None`, then ``anchored_position``
      is used to set the annotation line starting point, in widget size relative units
      (default is (0.0, 0.0)).
    :type anchor_point: Tuple[float, float]

    :param anchored_position: pixel position starting point for the annotation line
     where ``anchored_position`` is an (x,y) tuple in pixel units relative to the
     upper left corner of the widget, in pixel units (default is None).
    :type anchored_position: Tuple[int, int]

    :param position_offset: Used to *nudge* the line position to where you want, this
     is an (x,y) pixel offset added to the annotation line starting
     point, either set by ``anchor_point`` or ``anchored_position`` (in pixel units).
    :type position_offset: Tuple[int, int]

    :param int delta_x: the pixel x-offset for the second end of the line where the text
      will reside, in pixel units (default: -15).
    :param int delta_y: the pixel y-offset for the second end of the line where the text
      will reside, in pixel units (default: -10).

    :param int stroke: the annotation line width (in pixels). [NOT currently implemented]

    :param int line_color: the color of the annotation line (default: 0xFFFFFF).
    :param int text_color: the color of the text, if set to `None` color will be
      set to ``line_color`` (default: same as ``line_color``).

    :param text_offset: a (x,y) pixel offset to adjust text position relative
      to annotation line, in pixel units (default: (0,-1)).
    :type text_offset: Tuple[int, int]

    :param Boolean text_under: set `True` for text to be placed below the
      annotation line (default: False).

    .. figure:: annotation_example.png
      :scale: 125 %
      :align: center
      :alt: Example of the annotation widget.

      Example of the annotation widget showing two widget
      annotations (using ``widget`` and ``anchor_point`` input parameters) and a
      freeform annotation (using ``x`` and ``y`` input parameters).

      File location: *examples/displayio_layout_annotation_simpletest.py*
    """

    def __init__(
        self,
        x=None,
        y=None,
        text=None,
        font=FONT,
        delta_x=-15,
        delta_y=-10,
        widget=None,
        anchor_point=(0.0, 0.0),
        anchored_position=None,
        position_offset=(0, 0),
        stroke=3,  # Not currently implemented in adafruit_display_shapes/line.py
        line_color=0xFFFFFF,
        text_color=None,
        text_offset=(0, -1),
        text_under=False,
    ):

        if widget:
            if (x is not None) or (y is not None):
                print(
                    "Note: Overriding (x,y) values with widget, anchor_point"
                    " and/or anchored_position"
                )
            widget_width = widget.bounding_box[2]
            widget_height = widget.bounding_box[3]
            if anchor_point is not None:
                line_x0 = (
                    widget.x
                    + round(widget_width * anchor_point[0])
                    + position_offset[0]
                )
                line_y0 = (
                    widget.y
                    + round(widget_height * anchor_point[1])
                    + position_offset[1]
                )
            elif anchored_position is not None:
                line_x0 = widget.x + anchored_position[0] + position_offset[0]
                line_y0 = widget.y + anchored_position[1] + position_offset[1]
            else:
                raise ValueError("Must supply either anchor_point or anchored_position")
        elif (x is not None) and (y is not None):
            line_x0 = x
            line_y0 = y
        else:
            raise ValueError(
                "Must supply either (x,y) or widget and anchor_point or anchored_position"
            )

        line_x1 = line_x0 + delta_x
        line_y1 = line_y0 + delta_y

        text_anchor_point = (0.0, 1.0)  # default: set text anchor to left corner
        underline_x_multiplier = 1

        if delta_x < 0:  # line is heading to the left, set text anchor to right corner
            text_anchor_point = (1.0, 1.0)
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
        # 0. Line0 - from (x,y) to (x+delta_x, y+delta_y)
        # 1. Line1 - horizontal line for text
        # 2. Label

        self.append(self._line0)
        self.append(self._line1)
        self.append(self._label)
