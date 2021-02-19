# SPDX-FileCopyrightText: 2021 Kevin Matocha
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


class Control:
    """A Control class for responsive elements, including several response functions,
    including for touch response.

    **IMPORTANT**: The *touch_point* for all functions should be in local coordinates for this item.
      That means, any widget should adjust for self.x and self.y before passing
      the touchpoint up to this superclass function.

    """

    def __init__(
        self,
    ):
        self.touch_boundary = (
            None  # `self.touch_boundary` should be updated by the subclass
        )

    def contains(self, touch_point):
        """Checks if the Control was touched.  Returns True if the touch_point is within the Control's touch_boundary.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :return: Boolean

        """
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
        :return: None

        """
        pass

    def still_touched(self, touch_point):  # *** this needs a clearer name
        """Response function when Control remains touched. Should be overridden by subclass.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :return: None

        """
        pass

    def released(self, touch_point):
        """Response function when Control is released. Should be overridden by subclass.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :return: None

        """
        pass

    def gesture_response(self, gesture):
        """Response function to handle gestures (for future expansion). Should be
        overridden by subclass.

        :param gesture: To be defined
        :return: None

        """
        pass
