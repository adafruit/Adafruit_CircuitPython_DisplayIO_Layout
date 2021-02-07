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
# CircuitPython GUI Control Class for touch-related elements
#
# Defines the key response functions for touch controls:
#   - contains: evaluates if touch_point is within the Control's self.touch_boundary
#   - selected
#   - still_touched
#   - released
#   - gesture_response


class Control:
    """A Control class for responsive elements, including several response functions,
    including for touch response."""

    def __init__(
        self,
    ):

        self.touch_boundary = None  # should be overridden by subclass

    def contains(self, touch_point):
        """Checks if the Control was touched.  Returns True if the touch_point
        is within the Control's touch_boundary."""

        # The touch_point should be in local coordinates for this item.

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
        """Response function when Control is selected."""
        pass

    def still_touched(self, touch_point):  # *** this needs a clearer name
        """Response function when Control remains touched."""
        pass

    def released(self, touch_point):
        """Response function when Control is released."""
        pass

    def gesture_response(self, gesture):
        """Response function to handle gestures (future expansion)."""
        pass
