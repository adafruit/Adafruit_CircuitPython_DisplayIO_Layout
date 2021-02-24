# SPDX-FileCopyrightText: 2021 Kevin Matocha, Tim Cocks
#
# SPDX-License-Identifier: MIT

"""
`control`
================================================================================
CircuitPython GUI Control Class for touch-related elements

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"

# pylint: disable=unsubscriptable-object, unnecessary-pass


class Control:
    """A Control class for responsive elements, including touch response functions for displays.

    **IMPORTANT**: The *touch_point* for all functions should be in local coordinates
      for this item. That means, any widget should adjust the touchpoint for self.x and
      self.y before passing the touchpoint to this set of Control functions.

    The Control class uses a state variable **touch_boundary** [x, y, width, height]
    that defines the rectangular boundary for touch inputs.  The **touch_boundary**
    is used by the `contains` function to check when touches are within the Control's
    boundary.  Note: These **touch_boundary** dimensions are in the Control's local
    pixel coordinates.  The **x** and **y** values define the upper left corner of the
    **touch_boundary**.  The **touch_boundary** value should be updated by the sublcass
    definiton.

    """

    def __init__(
        self,
    ):
        self.touch_boundary = (
            None  # `self.touch_boundary` should be updated by the subclass
        )
        # Tuple of [x, y, width, height]: [int, int, int, int] all in pixel units
        # where x,y define the upper left corner
        # and width and height define the size of the `touch_boundary`

    def contains(self, touch_point):
        """Checks if the Control was touched.  Returns True if the touch_point is within the
         Control's touch_boundary.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :type touch_point: Tuple[x,y]
        :return: Boolean

        """

        # Note: if a widget's `scale` property is > 1, be sure to update the
        # `touch_boundary` dimensions to accommodate the `scale` factor
        if (self.touch_boundary is not None) and (
            (
                self.touch_boundary[0]
                <= touch_point[0]
                <= (self.touch_boundary[0] + self.touch_boundary[2])
            )
            and (
                self.touch_boundary[1]
                <= touch_point[1]
                <= (self.touch_boundary[1] + self.touch_boundary[3])
            )
        ):
            return True
        return False

    # place holder touch_handler response functions
    def selected(self, touch_point):
        """Response function when Control is selected. Should be overridden by subclass.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :type touch_point: Tuple[x,y]
        :return: None

        """
        pass
