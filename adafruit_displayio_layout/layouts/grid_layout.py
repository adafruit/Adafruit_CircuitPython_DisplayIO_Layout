# SPDX-FileCopyrightText: 2020 Kevin Matocha, Tim Cocks
#
# SPDX-License-Identifier: MIT

"""
`grid_layout`
================================================================================

A layout that organizes children into a grid table structure.


* Author(s): Kevin Matocha, Tim Cocks

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


class GridLayout(displayio.Group):

    """
    A layout that organizes children into a grid table structure.

    :param int x: x location the layout should be placed
    :param int y: y location the layout should be placed
    """

    # pylint: disable=too-many-arguments
    def __init__(self, x, y, width, height, grid_size, child_padding, max_children=4):
        super().__init__(x=x, y=y, max_size=max_children)
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self.grid_size = grid_size
        self.child_padding = child_padding
        self._sub_views = []

    def _layout_sub_views(self):

        for sub_view in self._sub_views:
            if sub_view["view"] not in self:
                grid_size_x = self.grid_size[0]
                grid_size_y = self.grid_size[1]

                grid_position_x = sub_view["grid_position"][0]
                grid_position_y = sub_view["grid_position"][1]

                button_size_x = sub_view["view_grid_size"][0]
                button_size_y = sub_view["view_grid_size"][1]

                print(
                    "setting width to: {}".format(
                        int(button_size_x * self._width / grid_size_x)
                        - 2 * self.child_padding
                    )
                )
                sub_view["view"].width = (
                    int(button_size_x * self._width / grid_size_x)
                    - 2 * self.child_padding
                )
                sub_view["view"].height = (
                    int(button_size_y * self._height / grid_size_y)
                    - 2 * self.child_padding
                )

                sub_view["view"].x = (
                    int(grid_position_x * self._width / grid_size_x)
                    + self.child_padding
                )
                sub_view["view"].y = (
                    int(grid_position_y * self._height / grid_size_y)
                    + self.child_padding
                )

                self.append(sub_view["view"])

    def add_sub_view(self, new_view, grid_position, view_grid_size):
        """Add a child to the grid.

        :param new_view: the child object to add e.g. label, button, etc...
        :param grid_position: where in the grid it should go. Tuple with
         x,y coordinates in grid cells. e.g. (1,0)
        :param view_grid_size: the size and shape of cells that the new
         child should occupy.
        :return: None"""
        sub_view_obj = {
            "view": new_view,
            "grid_position": grid_position,
            "view_grid_size": view_grid_size,
        }
        self._sub_views.append(sub_view_obj)
        self._layout_sub_views()
