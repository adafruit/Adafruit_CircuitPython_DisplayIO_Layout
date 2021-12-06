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
try:
    # Used only for typing
    from typing import Tuple
except ImportError:
    pass

import math
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
    :param bool divider_lines: Whether or not to draw lines between the cells.
    :param Union[tuple, list] h_divider_line_rows: Row indexes to draw divider
      lines above. Row indexes are 0 based.
    :param Union[tuple, list] v_divider_line_cols: Column indexes to draw divider
      lines before. Column indexes are 0 based.
    :param divider_line_color: The color of the divider lines (in hexadecimal)
    :param tuple cell_anchor_point: Anchor point used within every cell. Needs to
      be a tuple containing two floats between 0.0 and 1.0. Default is (0.0, 0.0)
      which will anchor content to the top left of the cell.

    """

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        x,
        y,
        width,
        height,
        grid_size,
        cell_padding=0,
        divider_lines=False,
        h_divider_line_rows=None,
        v_divider_line_cols=None,
        divider_line_color=0xFFFFFF,
        cell_anchor_point=(0.0, 0.0),
    ):
        super().__init__(x=x, y=y)
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self.grid_size = grid_size
        self.cell_padding = cell_padding
        self._cell_content_list = []
        self._cell_anchor_point = cell_anchor_point

        self._divider_lines = []
        self._divider_color = divider_line_color
        self.h_divider_line_rows = h_divider_line_rows
        self.v_divider_line_cols = v_divider_line_cols

        self._divider_lines_enabled = (
            (divider_lines is True)
            or (h_divider_line_rows is not None)
            or (v_divider_line_cols is not None)
        )

        if divider_lines:
            if self.h_divider_line_rows is None:
                self.h_divider_line_rows = []
                for _y in range(self.grid_size[1] + 1):
                    self.h_divider_line_rows.append(_y)
            if self.v_divider_line_cols is None:
                self.v_divider_line_cols = []
                for _x in range(self.grid_size[0] + 1):
                    self.v_divider_line_cols.append(_x)
        else:
            if not h_divider_line_rows:
                self.h_divider_line_rows = tuple()
            if not v_divider_line_cols:
                self.v_divider_line_cols = tuple()

        # use at least 1 padding so that content is inside the divider lines
        if cell_padding == 0 and (
            divider_lines or h_divider_line_rows or v_divider_line_cols
        ):
            self.cell_padding = 1

    def _layout_cells(self):
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        for cell in self._cell_content_list:
            if cell["content"] not in self:
                grid_size_x = self.grid_size[0]
                grid_size_y = self.grid_size[1]

                grid_position_x = cell["grid_position"][0]
                grid_position_y = cell["grid_position"][1]

                content_cell_size_x = cell["cell_size"][0]
                content_cell_size_y = cell["cell_size"][1]

                _measured_width = (
                    math.ceil(content_cell_size_x * self._width / grid_size_x)
                    - 2 * self.cell_padding
                )

                _measured_height = (
                    math.ceil(content_cell_size_y * self._height / grid_size_y)
                    - 2 * self.cell_padding
                )

                if hasattr(cell["content"], "resize"):
                    # if it has resize function
                    cell["content"].resize(
                        _measured_width,
                        _measured_height,
                    )
                else:
                    try:
                        # try width and height properties.
                        cell["content"].width = _measured_width
                        cell["content"].height = _measured_height
                    except AttributeError:
                        # This element does not allow setting width and height.
                        # No problem, we'll use whatever size it already is.
                        # _measured_width = cell["content"].width
                        # _measured_height = cell["content"].height

                        pass

                if not hasattr(cell["content"], "anchor_point"):

                    cell["content"].x = (
                        int(grid_position_x * self._width / grid_size_x)
                        + self.cell_padding
                        + int(cell["cell_anchor_point"][0] * _measured_width)
                        - int(cell["content"].width * cell["cell_anchor_point"][0])
                    )
                    cell["content"].y = (
                        int(grid_position_y * self._height / grid_size_y)
                        + self.cell_padding
                        + int(cell["cell_anchor_point"][1] * _measured_height)
                        - int(cell["content"].height * cell["cell_anchor_point"][1])
                    )
                else:
                    cell["content"].anchor_point = cell["cell_anchor_point"]
                    cell["content"].anchored_position = (
                        int(grid_position_x * self._width / grid_size_x)
                        + self.cell_padding
                        + (cell["cell_anchor_point"][0] * _measured_width),
                        int(grid_position_y * self._height / grid_size_y)
                        + self.cell_padding
                        + (cell["cell_anchor_point"][1] * _measured_height),
                    )

                self.append(cell["content"])

                if self._divider_lines_enabled:
                    palette = displayio.Palette(2)
                    palette[0] = self._divider_color
                    palette[1] = self._divider_color

                    if not hasattr(cell["content"], "anchor_point"):
                        _bottom_line_loc_y = (
                            (cell["content"].y + _measured_height + self.cell_padding)
                            - 1
                            - int(cell["cell_anchor_point"][1] * _measured_height)
                            + int(cell["content"].height * cell["cell_anchor_point"][1])
                        )

                        _bottom_line_loc_x = (
                            cell["content"].x
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][0] * _measured_width)
                            + int(cell["content"].width * cell["cell_anchor_point"][0])
                        )

                        _top_line_loc_y = (
                            cell["content"].y
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][1] * _measured_height)
                            + int(cell["content"].height * cell["cell_anchor_point"][1])
                        )

                        _top_line_loc_x = (
                            cell["content"].x
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][0] * _measured_width)
                            + int(cell["content"].width * cell["cell_anchor_point"][0])
                        )

                        _right_line_loc_y = (
                            cell["content"].y
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][1] * _measured_height)
                            + int(cell["content"].height * cell["cell_anchor_point"][1])
                        )

                        _right_line_loc_x = (
                            (cell["content"].x + _measured_width + self.cell_padding)
                            - 1
                            - int(cell["cell_anchor_point"][0] * _measured_width)
                            + int(cell["content"].width * cell["cell_anchor_point"][0])
                        )
                    else:
                        _bottom_line_loc_y = (
                            cell["content"].anchored_position[1]
                            + _measured_height
                            + self.cell_padding
                            - (cell["cell_anchor_point"][1] * _measured_height)
                        ) - 1
                        _bottom_line_loc_x = (
                            cell["content"].anchored_position[0]
                            - self.cell_padding
                            - (cell["cell_anchor_point"][0] * _measured_width)
                        )

                        _top_line_loc_y = (
                            cell["content"].anchored_position[1]
                            - self.cell_padding
                            - (cell["cell_anchor_point"][1] * _measured_height)
                        )
                        _top_line_loc_x = (
                            cell["content"].anchored_position[0]
                            - self.cell_padding
                            - (cell["cell_anchor_point"][0] * _measured_width)
                        )

                        _right_line_loc_y = (
                            cell["content"].anchored_position[1]
                            - self.cell_padding
                            - (cell["cell_anchor_point"][1] * _measured_height)
                        )
                        _right_line_loc_x = (
                            (
                                cell["content"].anchored_position[0]
                                + _measured_width
                                + self.cell_padding
                            )
                            - 1
                            - (cell["cell_anchor_point"][0] * _measured_width)
                        )

                    _horizontal_divider_line = displayio.Shape(
                        _measured_width + (2 * self.cell_padding),
                        1,
                        mirror_x=False,
                        mirror_y=False,
                    )

                    _bottom_divider_tilegrid = displayio.TileGrid(
                        _horizontal_divider_line,
                        pixel_shader=palette,
                        y=_bottom_line_loc_y,
                        x=_bottom_line_loc_x,
                    )

                    _top_divider_tilegrid = displayio.TileGrid(
                        _horizontal_divider_line,
                        pixel_shader=palette,
                        y=_top_line_loc_y,
                        x=_top_line_loc_x,
                    )

                    _vertical_divider_line = displayio.Shape(
                        1,
                        _measured_height + (2 * self.cell_padding),
                        mirror_x=False,
                        mirror_y=False,
                    )

                    _left_divider_tilegrid = displayio.TileGrid(
                        _vertical_divider_line,
                        pixel_shader=palette,
                        y=_top_line_loc_y,
                        x=_top_line_loc_x,
                    )

                    _right_divider_tilegrid = displayio.TileGrid(
                        _vertical_divider_line,
                        pixel_shader=palette,
                        y=_right_line_loc_y,
                        x=_right_line_loc_x,
                    )

                    for line_obj in self._divider_lines:
                        self.remove(line_obj["tilegrid"])

                    """
                    Only use bottom divider lines on the bottom row. All
                    other rows rely on top divder lines of the row beneath them.
                    Add the content_cell_size to the grid_position to account for
                    areas larger than 1x1 cells. For 1x1 cells this will equal zero
                    and not change anything.
                    """
                    if (
                        grid_position_y + content_cell_size_y - 1
                    ) == grid_size_y - 1 and (
                        (grid_position_y + content_cell_size_y - 1) + 1
                        in self.h_divider_line_rows
                    ):
                        self._divider_lines.append(
                            {
                                "shape": _horizontal_divider_line,
                                "tilegrid": _bottom_divider_tilegrid,
                            }
                        )

                    """
                    Every cell whose index is in h_divider_line_rows gets
                    a top divider line.
                    """
                    if grid_position_y in self.h_divider_line_rows:
                        self._divider_lines.append(
                            {
                                "shape": _horizontal_divider_line,
                                "tilegrid": _top_divider_tilegrid,
                            }
                        )

                    """
                    Every cell whose index is in v_divider_line_cols gets
                    a left divider line.
                    """
                    if grid_position_x in self.v_divider_line_cols:
                        self._divider_lines.append(
                            {
                                "shape": _horizontal_divider_line,
                                "tilegrid": _left_divider_tilegrid,
                            }
                        )
                    """
                    Only use right divider lines on the right-most column. All
                    other columns rely on left divider lines of the column to their
                    left. Add the content_cell_size to the grid_position to account for
                    areas larger than 1x1 cells. For 1x1 cells this will equal zero
                    and not change anything.
                    """
                    if (
                        grid_position_x + content_cell_size_x - 1
                    ) == grid_size_x - 1 and (
                        (grid_position_x + content_cell_size_x - 1) + 1
                        in self.v_divider_line_cols
                    ):
                        self._divider_lines.append(
                            {
                                "shape": _vertical_divider_line,
                                "tilegrid": _right_divider_tilegrid,
                            }
                        )

                    for line_obj in self._divider_lines:
                        self.append(line_obj["tilegrid"])

    def add_content(
        self, cell_content, grid_position, cell_size, cell_anchor_point=None
    ):
        """Add a child to the grid.

        :param cell_content: the content to add to this cell e.g. label, button, etc...
         Group subclass that have width and height properties can be used.
        :param tuple grid_position: where in the grid it should go. Tuple with
         x,y coordinates in grid cells. e.g. (1,0)
        :param tuple cell_size: the size and shape that the new cell should
         occupy. Width and height in cells inside a tuple e.g. (1, 1)
        :param tuple cell_anchor_point: a tuple of floats between 0.0 and 1.0.
         If passed, this value will override the cell_anchor_point of the GridLayout
         for the single cell having it's content added with this function call. If omitted
         then the cell_anchor_point from the GridLayout will be used.
        :return: None"""

        if cell_anchor_point:
            _this_cell_anchor_point = cell_anchor_point
        else:
            _this_cell_anchor_point = self._cell_anchor_point

        sub_view_obj = {
            "cell_anchor_point": _this_cell_anchor_point,
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

    @property
    def cell_size_pixels(self) -> Tuple[int, int]:
        """
        Get the size of a 1x1 cell in pixels. Can be useful for manually
        re-positioning content within cells.

        :return Tuple[int, int]: A tuple containing the (x, y) size in
          pixels of a 1x1 cell in the GridLayout
        """
        return (self._width // self.grid_size[0], self._height // self.grid_size[1])
