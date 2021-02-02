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
#
# CircuitPython GUI Widget Class for visual elements
#
# Properties:
#   - width
#   - height
#   - name
#   - anchor_point
#   - anchored_position

import displayio


class Widget(displayio.Group):
    """A Widget class definition for graphical display elements.

    :param int x: pixel position
    :param int y: pixel position
    :param int width: width of the switch in pixels, set to ``None`` to auto-size
     relative to the height
    :param int height: height of the switch in pixels
    :param str name: name of the switch
    :param float anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor
     point relative to the switch bounding box
    :param int anchored_position: (x,y) pixel value for the location
     of the anchor_point"""

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

        super().__init__(**kwargs)  # should send x,y and scale (optional) to Group

        self._width = width
        self._height = height
        self.name = name
        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        # self.bounding_box: pixel extent of the widget [x0, y0, width, height]
        if bounding_box is None:
            if (width is not None) and (height is not None):
                self._bounding_box = [0, 0, width, height]
            else:
                self._bounding_box = [0, 0, 0, 0]

        self._update_position

    def _update_position(self):
        # Reposition self.x, self.y based on anchor_point and anchored_position
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
        """The anchor point for positioning the switch, works in concert with `anchored_position`."""
        return self._anchor_point

    @anchor_point.setter
    def anchor_point(self, new_anchor_point):
        self._anchor_point = new_anchor_point
        self._update_position()

    @property
    def anchored_position(self):
        """The anchored position for positioning the switch, works in concert with `anchor_point`."""
        return self._anchored_position

    @anchored_position.setter
    def anchored_position(self, new_anchored_position):
        self._anchored_position = new_anchored_position
        self._update_position()

    @property
    def bounding_box(self):
        """The boundary of the widget. [x, y, width, height] in widget coordinates."""
        return self._bounding_box

    @property
    def width(self):
        """The widget width, in pixels. Must be defined at instance."""
        return self._width

    @property
    def height(self):
        """The widget height, in pixels. Must be defined at instance."""
        return self._height
