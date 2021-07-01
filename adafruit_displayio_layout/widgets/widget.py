# SPDX-FileCopyrightText: 2021 Kevin Matocha, Tim Cocks
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

# pylint: disable=too-many-arguments


class Widget(displayio.Group):
    """
    A Widget class definition for graphical display elements.  The Widget handles
    the sizing and positioning of the widget.

    :param int x: pixel position
    :param int y: pixel position
    :param int width: width of the widget in pixels, set to None to auto-size relative to
     the height
    :param int height: height of the widget in pixels
    :param anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor point relative to the
     widget bounding box
    :type anchor_point: Tuple[float,float]
    :param int anchored_position: (x,y) pixel value for the location of the anchor_point
    :type anchored_position: Tuple[int, int]


    .. figure:: gui_layout_coordinates.png
      :scale: 50 %
      :alt: Diagram of layout coordinates

      Diagram showing the global and local coordinate systems and the Widget's
      associated class variables.

    **Widget Class Positioning: Display vs. Local Coordinates**

    The Widget class is used to define the position and size of the graphical elements
    that define the widget.
    The Widget is a subclass of `displayio.Group` and inherits the positioning elements
    of `displayio.Group`, including *x*, *y* (in pixels).  If the Widget is directly added
    to the display, then the *.x* and *.y* positions refer to the pixel position on
    the display. (Note: If the Widget is actually held within another Group, then the *.x*
    and *.y* of the widget are in that Group's local coordinate system.)

    This Widget coordinate system is illustrated in the diagram above, showing the
    coordinate systems of a sliding switch widget.  The display's origin (x=0, y=0)
    is at the upper left corner of the display.  In this example the display size is
    320 x 240 pixels, so the display's bottom right corner is at display coordinates
    (x=320, y=240). The upper left corner of the widget is labeled notionally as
    *widget.x* and *widget.y* is set at the display pixel position of (x=100, y=50).


    **Local Coordinates: bounding_box**

    Other parameters defined in the Widget class use a "local" coordinate system, as
    indicated by the red text in the display.  These include `bounding_box` and
    *touch_boundary*.  The `bounding_box` defines the origin of a Widget is at the upper
    left corner of the key graphical element of the widget and is set to (0,0) in
    widget local coordinates.  The `width` and `height` of the `bounding_box` are
    defined as the pixel distances that make a mininum box that contains the key
    graphical elements of the widget. In the case of this example, the width is
    100 pixels and the height is 40 pixels.  (Note: If a label is included for a
    widget, the label should not be included in the `bounding_box`.)

    **Local Coordinates: touch_boundary (inherited from `Control` class)**
    This example of a sliding switch reacts to touch using the addition of
    inheritance from the `Control` class, so additional dimensional parameters are
    included for that class definition.  Similar to the definition of
    the `bounding_box`, the *touch_boundary* is also defined using the widget's
    local coordinate system.

    As shown in the diagram, we see that the *touch_boundary* is larger than the
    `bounding_box`.  The *touch_boundary* should likely be larger than the
    `bounding_box` since finger touches are not precise.  The use of additional
    space around the widget ensures that the widget reacts when the touch is close
    enough.  In the case of this example, the switch widget provides a *touch_padding*
    option to define additional space around the `bounding_box` where touches are
    accepted (with the `Control.contains()` function).  Looking at the example, we
    see that the upper left corner of the *touch_boundary* is (x=-10, y=-10) in widget
    local coordinates.  This means that the accepted touch boundary starts at 10 pixels
    up and 10 pixels left of the upper left corner of the widget.  The *touch_boundary*
    is 120 pixels wide and 60 pixels high.  This confirms that a 10 pixel *touch_padding*
    was used, giving additional 10 pixels around the `bounding_box`.  Note: If you are
    building your own new widgets, the *touch_boundary* tuple can be adjusted directly to
    meet whatever needs your widget needs.  The *touch_boundary* is used in the
    `Control.contains()` function to determine when the Control-type widget was touched.

    Note: If a widget does not need to respond to touches (for example a display of a
    value), then it should not inherit the `Control` class, and thus will not have a
    *touch_boundary*.

    **Positioning on the screen: Using x and y or anchor_point and anchored_position**

    The Widget class has several options for setting the widget position on the screen.
    In the simplest case, you can define the widget's *.x* and *.y* properties to set
    the position.  (**Reminder**: If your widget is directly shown by the display using
    *display.show(my_widget)*), then the *.x* and *.y* positions will be in the display's
    coordinate system.  But if your widget is held inside of another Group, then its
    coordinates will be in that Group's coordinate system.)

    The Widget class definition also allows for relative positioning on the screen using
    the combination of `anchor_point` and `anchored_position`. This method is useful
    when you want your widget to be centered or aligned along one of its edges.

    A good example of the use of `anchor_point` and `anchored_position` is in the
    `Adafruit "Candy Hearts" learn guide
    <https://learn.adafruit.com/circuit-python-tft-gizmo-candy-hearts/how-it-works>`_
    related to text positioning.

    The `anchor_point` is a Tuple (float, float) that corresponds to the fractional
    position of the size of the widget. The upper left corner being
    `anchor_point` =(0.0, 0.0) and the lower right corner being `anchor_point` =(1.0, 1.0).
    The center of the widget is then `anchor_point` =(0.5, 0.5), halfway along the
    x-size and halfway along the y-size.  One more example, the center of the bottom
    edge is (0.5, 1.0), halfway along the x-size and all the way of the y-size.

    Once you define the `anchor_point`, you can now set the `anchored_position`.  The
    `anchored_position` is the pixel dimension location where you want to put the
    `anchor_point`.  To learn from example, let's say I want to place my widget so
    its bottom right corner is at the bottom right of my display (assume 320 x 240
    pixel size display).

    First, I want to define the widget reference point to be the bottom right corner of
    my widget, so I'll set `anchor_point` =(1.0,1.0).  Next, I want that anchor point
    on the widget to be placed at the bottom right corner of my display, so I'll set
    `anchored_position` =(320,240).  In essence, the `anchor_point` is defining the
    reference ("anchor") point on the widget (but in relative widget-sized dimensions
    using x,y floats between 0.0 and 1.0) and then places that `anchor_point` at the
    pixel location specified as the `anchored_position` in pixel dimensions
    (x, y are in pixel units on the display).

    The reason for using `anchor_point` is so that you
    don't need to know the width or height of the widget in advance, you can use
    `anchor_point` and it will always adjust for the widget's height and width to
    set the position at the `anchored_position` pixel position.

    In summary:
     - `anchor_point` is x,y tuple (floats) of the relative size of the widget.  Upper left
        corner is (0.0, 0.0) and lower right is (1.0, 1.0).
     - `anchored_position` is in x,y tuple (ints) pixel coordinates where the `anchor_point`
        will be placed.

    """

    def __init__(
        self,
        x=0,
        y=0,
        scale=1,
        width=None,
        height=None,
        anchor_point=None,
        anchored_position=None,
    ):

        super().__init__(x=x, y=y, scale=scale)
        # send x,y and scale to Group
        #
        # If scale is set > 1, will need to update the Control `touch_boundary`
        # to accommodate the larger scale

        self._width = width
        self._height = height
        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        # self._bounding_box: pixel extent of the widget [x0, y0, width, height]
        # The bounding box should be updated based on the specifics of the widget
        if (width is not None) and (height is not None):
            self._bounding_box = [0, 0, width, height]
        else:
            self._bounding_box = [0, 0, 0, 0]

        self._update_position()

    def resize(self, new_width, new_height):
        """Resizes the widget dimensions (for use with automated layout functions).

        **IMPORTANT:** The `resize` function should be overridden by the subclass definition.

        The width and height are provided together so the subclass `resize`
        function can apply any constraints that require consideration of both width
        and height (such as maintaining a Widget's preferred aspect ratio).  The Widget should
        be resized to the maximum size that can fit within the dimensions defined by
        the requested *new_width* and *new_height*. After resizing, the Widget's
        `bounding_box` should also be updated.

        :param int new_width: target maximum width (in pixels)
        :param int new_height: target maximum height (in pixels)
        :return: None

        """
        self._width = new_width
        self._height = new_height

        self._bounding_box[2] = new_width
        self._bounding_box[3] = new_height

    def _update_position(self):
        """
        Widget class function for updating the widget's *x* and *y* position based
        upon the `anchor_point` and `anchored_position` values. The subclass should
        call `_update_position` after the widget is resized.

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
    def width(self):
        """The widget width, in pixels. (getter only)

        :return: int
        """
        return self._width

    @property
    def height(self):
        """The widget height, in pixels. (getter only)

        :return: int
        """
        return self._height

    @property
    def bounding_box(self):
        """The boundary of the widget. [x, y, width, height] in Widget's local
        coordinates (in pixels). (getter only)

        :return: Tuple[int, int, int, int]"""
        return self._bounding_box

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
