# SPDX-FileCopyrightText: 2020 Kevin Matocha, Tim Cocks
#
# SPDX-License-Identifier: MIT

"""
`grid_layout`
================================================================================

A layout that organizes cells into a grid table structure.


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

    :param int x: x location the layout should be placed. Pixel coordinates.
    :param int y: y location the layout should be placed. Pixel coordinates.
    :param int width: Width of the layout in pixels.
    :param int height: Height of the layout in pixels.
    :param tuple grid_size: Size in cells as two ints in a tuple e.g. (2, 2)
    :param int cell_padding: Extra padding space inside each cell. In pixels.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, x, y, width, height, grid_size, cell_padding):
        super().__init__(x=x, y=y)
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self.grid_size = grid_size
        self.cell_padding = cell_padding
        self._cell_content_list = []

    def _layout_cells(self):

        for cell in self._cell_content_list:
            if cell["content"] not in self:
                grid_size_x = self.grid_size[0]
                grid_size_y = self.grid_size[1]

                grid_position_x = cell["grid_position"][0]
                grid_position_y = cell["grid_position"][1]

                button_size_x = cell["cell_size"][0]
                button_size_y = cell["cell_size"][1]

                if hasattr(cell["content"], "resize"):
                    # if it has resize function
                    cell["content"].resize(
                        (
                            int(button_size_x * self._width / grid_size_x)
                            - 2 * self.cell_padding
                        ),
                        (
                            int(button_size_y * self._height / grid_size_y)
                            - 2 * self.cell_padding
                        ),
                    )
                else:
                    try:
                        # try width and height properties.
                        cell["content"].width = (
                            int(button_size_x * self._width / grid_size_x)
                            - 2 * self.cell_padding
                        )
                        cell["content"].height = (
                            int(button_size_y * self._height / grid_size_y)
                            - 2 * self.cell_padding
                        )
                    except AttributeError:
                        # This element does not allow setting width and height.
                        # No problem, we'll use whatever size it already is.
                        pass

                cell["content"].x = (
                    int(grid_position_x * self._width / grid_size_x) + self.cell_padding
                )
                cell["content"].y = (
                    int(grid_position_y * self._height / grid_size_y)
                    + self.cell_padding
                )

                self.append(cell["content"])

    def add_content(self, cell_content, grid_position, cell_size):
        """Add a child to the grid.

        :param cell_content: the content to add to this cell e.g. label, button, etc...
         Group subclass that have width and height properties can be used.
        :param tuple grid_position: where in the grid it should go. Tuple with
         x,y coordinates in grid cells. e.g. (1,0)
        :param tuple cell_size: the size and shape that the new cell should
         occupy. Width and height in cells inside a tuple e.g. (1, 1)
        :return: None"""
        sub_view_obj = {
            "content": cell_content,
            "grid_position": grid_position,
            "cell_size": cell_size,
        }
        self._cell_content_list.append(sub_view_obj)
        self._layout_cells()

    def get_cell(self, cell_coordinates):
        """
        Return a cells content based on the cell_coordinates. Raises
        KeyError if coordinates were not found in the GridLayout.

        :param tuple cell_coordinates: the coordinates to lookup in the grid
        :return: the displayio content object at those coordinates
        """
        for index, cell in enumerate(self._cell_content_list):
            if cell["grid_position"] == cell_coordinates:
                return self._cell_content_list[index]["content"]

        raise KeyError(
            "GridLayout does not contain cell at coordinates {}".format(
                cell_coordinates
            )
        )
