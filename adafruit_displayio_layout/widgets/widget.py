# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
"""

`widget`
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

import displayio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class Widget(displayio.Group):
    """
    A Widget class definition for graphical display elements.

    :param int x: pixel position
    :param int y: pixel position
    :param int width: width of the switch in pixels, set to ``None`` to auto-size
     relative to the height
    :param int height: height of the switch in pixels
    :param str name: name of the switch
    :param float anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor
     point relative to the switch bounding box
    :param int anchored_position: (x,y) pixel value for the location
     of the anchor_point

    """

    def __init__(
        self,
        width=None,
        height=None,
        name="",
        anchor_point=None,
        anchored_position=None,
        bounding_box=None,  # pixel extent of the widget [x0, y0, width, height]
        **kwargs,
    ):
        # pylint: disable=too-many-arguments

        super().__init__(**kwargs)  # should send x,y and scale (optional) to Group

        self._width = width
        self._height = height
        self.name = name
        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        # self._bounding_box: pixel extent of the widget [x0, y0, width, height]
        # The bounding box should be updated based on the specifics of the widget
        if bounding_box is None:
            if (width is not None) and (height is not None):
                self._bounding_box = [0, 0, width, height]
            else:
                self._bounding_box = [0, 0, 0, 0]

        self._update_position()

    def _update_position(self):
        """
        Internal Widget class function for updating the x,y position based upon
        the `anchor_point` and `anchored_position`.

        :return: None
        """

        if (self._anchor_point is not None) and (self._anchored_position is not None):
            self.x = (
                self._anchored_position[0]
                - int(self._anchor_point[0] * self._bounding_box[2])
                - self._bounding_box[0]
            )
            self.y = (
                self._anchored_position[1]
                - int(self._anchor_point[1] * self._bounding_box[3])
                - self._bounding_box[1]
            )

    @property
    def anchor_point(self):
        """The anchor point for positioning the widget, works in concert
        with `anchored_position`  The relative (X,Y) position of the widget where the
        anchored_position is placed.  For example (0.0, 0.0) is the Widget's upper left corner,
        (0.5, 0.5) is the Widget's center point, and (1.0, 1.0) is the Widget's lower right corner.

        :param anchor_point: In relative units of the Widget size.
        :type anchor_point: Tuple[float, float]"""
        return self._anchor_point

    @anchor_point.setter
    def anchor_point(self, new_anchor_point):
        self._anchor_point = new_anchor_point
        self._update_position()

    @property
    def anchored_position(self):
        """The anchored position (in pixels) for positioning the widget, works in concert
        with `anchor_point`.  The `anchored_position` is the x,y pixel position
        for the placement of the Widget's `anchor_point`.

        :param anchored_position: The (x,y) pixel position for the anchored_position (in pixels).
        :type anchored_position: Tuple[int, int]

        """
        return self._anchored_position

    @anchored_position.setter
    def anchored_position(self, new_anchored_position):
        self._anchored_position = new_anchored_position
        self._update_position()

    @property
    def bounding_box(self):
        """The boundary of the widget. [x, y, width, height] in Widget's local
        coordinates (in pixels)."""
        return self._bounding_box

    @property
    def width(self):
        """The widget width, in pixels."""
        return self._width

    @property
    def height(self):
        """The widget height, in pixels."""
        return self._height

    def resize(self, new_width, new_height):
        """Resizes the widget dimensions for use with automated layout functions.

        **The `resize` function should be overridden by the subclass definition.**

        The width and height are provided together so the subclass `resize`
        function can apply any constraints that require consideration of both width
        and height (such as maintaining a preferred aspect ratio).  The Widget should
        be resized to the maximum size that can fit within the dimensions defined by
        the requested *new_width* and *new_height*. After resizing, the Widget
        `bounding_box` should also be updated.

        :param int new_width: target maximum width (in pixels)
        :param int new_height: target maximum height (in pixels)
        :return: None

        """
        self._width = new_width
        self._height = new_height
