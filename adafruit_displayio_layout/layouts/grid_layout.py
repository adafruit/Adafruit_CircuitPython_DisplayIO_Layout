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
    from typing import Any, List, Optional, Tuple, Union
except ImportError:
    pass

import math
import displayio
from vectorio import Rectangle

__version__ = "0.0.0+auto.0"
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
        x: int,
        y: int,
        width: int,
        height: int,
        grid_size: tuple[int, int],
        cell_padding: int = 0,
        divider_lines: bool = False,
        h_divider_line_rows: Union[Tuple[int, ...], List[int], None] = None,
        v_divider_line_cols: Union[Tuple[int, ...], List[int], None] = None,
        divider_line_color: int = 0xFFFFFF,
        cell_anchor_point: Tuple[float, float] = (0.0, 0.0),
    ) -> None:
        super().__init__(x=x, y=y)
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self.grid_size = grid_size
        self.cell_padding = cell_padding
        self._cell_content_list: List[dict[str, Any]] = []
        self._cell_anchor_point = cell_anchor_point

        self._divider_lines: List[dict[str, Any]] = []
        self._divider_color = divider_line_color
        self.h_divider_line_rows = h_divider_line_rows or tuple()
        self.v_divider_line_cols = v_divider_line_cols or tuple()

        self._divider_lines_enabled = (
            (divider_lines is True)
            or (h_divider_line_rows is not None)
            or (v_divider_line_cols is not None)
        )

        if divider_lines:
            if h_divider_line_rows is None:
                self.h_divider_line_rows = []
                for _y in range(self.grid_size[1] + 1):
                    self.h_divider_line_rows.append(_y)
            if v_divider_line_cols is None:
                self.v_divider_line_cols = []
                for _x in range(self.grid_size[0] + 1):
                    self.v_divider_line_cols.append(_x)

        # use at least 1 padding so that content is inside the divider lines
        if cell_padding == 0 and (
            divider_lines or h_divider_line_rows or v_divider_line_cols
        ):
            self.cell_padding = 1

    def layout_cells(self):
        """render the grid with all cell content and dividers"""
        self._layout_cells()

    def _layout_cells(self) -> None:
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        for line_obj in self._divider_lines:
            self.remove(line_obj["rect"])
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
                        + int(cell["cell_anchor_point"][0] * _measured_width),
                        int(grid_position_y * self._height / grid_size_y)
                        + self.cell_padding
                        + int(cell["cell_anchor_point"][1] * _measured_height),
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
                            - int(cell["cell_anchor_point"][1] * _measured_height)
                        ) - 1
                        _bottom_line_loc_x = (
                            cell["content"].anchored_position[0]
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][0] * _measured_width)
                        )

                        _top_line_loc_y = (
                            cell["content"].anchored_position[1]
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][1] * _measured_height)
                        )
                        _top_line_loc_x = (
                            cell["content"].anchored_position[0]
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][0] * _measured_width)
                        )

                        _right_line_loc_y = (
                            cell["content"].anchored_position[1]
                            - self.cell_padding
                            - int(cell["cell_anchor_point"][1] * _measured_height)
                        )
                        _right_line_loc_x = (
                            (
                                cell["content"].anchored_position[0]
                                + _measured_width
                                + self.cell_padding
                            )
                            - 1
                            - int(cell["cell_anchor_point"][0] * _measured_width)
                        )

                    _bottom_divider_rect = Rectangle(
                        pixel_shader=palette,
                        width=_measured_width + (2 * self.cell_padding),
                        height=1,
                        y=_bottom_line_loc_y,
                        x=_bottom_line_loc_x,
                    )

                    _top_divider_rect = Rectangle(
                        width=_measured_width + (2 * self.cell_padding),
                        height=1,
                        pixel_shader=palette,
                        y=_top_line_loc_y,
                        x=_top_line_loc_x,
                    )

                    _left_divider_rect = Rectangle(
                        pixel_shader=palette,
                        width=1,
                        height=_measured_height + (2 * self.cell_padding),
                        y=_top_line_loc_y,
                        x=_top_line_loc_x,
                    )

                    _right_divider_rect = Rectangle(
                        pixel_shader=palette,
                        width=1,
                        height=_measured_height + (2 * self.cell_padding),
                        y=_right_line_loc_y,
                        x=_right_line_loc_x,
                    )

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
                                "rect": _bottom_divider_rect,
                            }
                        )

                    """
                    Every cell whose index is in h_divider_line_rows gets
                    a top divider line.
                    """
                    if grid_position_y in self.h_divider_line_rows:
                        self._divider_lines.append(
                            {
                                "rect": _top_divider_rect,
                            }
                        )

                    """
                    Every cell whose index is in v_divider_line_cols gets
                    a left divider line.
                    """
                    if grid_position_x in self.v_divider_line_cols:
                        self._divider_lines.append(
                            {
                                "rect": _left_divider_rect,
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
                                "rect": _right_divider_rect,
                            }
                        )

        for line_obj in self._divider_lines:
            self.append(line_obj["rect"])

    def add_content(
        self,
        cell_content: displayio.Group,
        grid_position: Tuple[int, int],
        cell_size: Tuple[int, int],
        cell_anchor_point: Optional[Tuple[float, ...]] = None,
        layout_cells=True,
    ) -> None:
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
        if layout_cells:
            self._layout_cells()

    def get_cell(self, cell_coordinates: Tuple[int, int]) -> displayio.Group:
        """
        Return a cells content based on the cell_coordinates. Raises
        KeyError if coordinates were not found in the GridLayout.

        :param tuple cell_coordinates: the coordinates to lookup in the grid
        :return: the displayio content object at those coordinates
        """
        for index, cell in enumerate(self._cell_content_list):
            # exact location 1x1 cell
            if cell["grid_position"] == cell_coordinates:
                return self._cell_content_list[index]["content"]

            # multi-spanning cell, any size bigger than 1x1
            if (
                cell["grid_position"][0]
                <= cell_coordinates[0]
                < cell["grid_position"][0] + cell["cell_size"][0]
                and cell["grid_position"][1]
                <= cell_coordinates[1]
                < cell["grid_position"][1] + cell["cell_size"][1]
            ):
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

    @property
    def width(self) -> int:
        """
        The width in pixels of the GridLayout.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The height in pixels of the GridLayout.
        """
        return self._height

    def which_cell_contains(
        self, pixel_location: Union[Tuple[int, int], List[int]]
    ) -> Optional[tuple]:
        """
        Given a pixel x,y coordinate returns the location of the cell
        that contains the coordinate.

        :param pixel_location: x,y pixel coordinate as a tuple or list
        :returns: cell coordinates x,y tuple or None if the pixel coordinates are
            outside the bounds of the GridLayout
        """
        cell_size = self.cell_size_pixels
        if (
            not self.x <= pixel_location[0] < self.x + self.width
            or not self.y <= pixel_location[1] < self.y + self.height
        ):
            return None

        cell_x_coord = (pixel_location[0] - self.x) // cell_size[0]
        cell_y_coord = (pixel_location[1] - self.y) // cell_size[1]

        return cell_x_coord, cell_y_coord
