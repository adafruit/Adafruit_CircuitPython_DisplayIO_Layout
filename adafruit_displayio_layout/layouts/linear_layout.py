# SPDX-FileCopyrightText: Copyright (c) 2021 Tim Cocks
#
# SPDX-License-Identifier: MIT
"""
`linear_layout`
================================================================================

A layout that organizes cells into a vertical or horizontal line.


* Author(s): Tim Cocks

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

from adafruit_displayio_layout.widgets.widget import Widget


class LinearLayout(Widget):
    """
    LinearLayout holds multiple content elements and arranges
    them in a line either horizontally or vertically.
    """

    VERTICAL_ORIENTATION = 1
    HORIZONTAL_ORIENTATION = 2

    def __init__(
        self,
        x,
        y,
        orientation=VERTICAL_ORIENTATION,
        padding=0,
    ):
        """
        :param int x: The horizontal position of the layout
        :param int y: The vertical position of the layout
        :param int orientation: The orientation of the layout. Must be VERTICAL_ORIENTATION
         or HORIZONTAL_ORIENTATION
        :param int padding: The padding between items in the layout
        """

        super().__init__(x=x, y=y, width=1, height=1)

        self.x = x
        self.y = y
        self.padding = padding
        if orientation not in [self.VERTICAL_ORIENTATION, self.HORIZONTAL_ORIENTATION]:
            raise ValueError(
                "Orientation must be either LinearLayout.VERTICAL_ORIENTATION"
                " or LinearLayout.HORIZONTAL_ORIENTATION"
            )

        self.orientation = orientation
        self._content_list = []
        self._prev_content_end = 0

    def add_content(self, content):
        """Add a child to the linear layout.

        :param content: the content to add to the linear layout e.g. label, button, etc...
         Group subclasses that have width and height properties can be used.

        :return: None"""

        self._content_list.append(content)
        self.append(content)
        self._layout()

    def _layout(self):
        # pylint: disable=too-many-branches, protected-access
        self._prev_content_end = 0

        for _, content in enumerate(self._content_list):
            if not hasattr(content, "anchor_point"):
                if self.orientation == self.VERTICAL_ORIENTATION:
                    content.y = self._prev_content_end
                    try:
                        self._prev_content_end = (
                            self._prev_content_end + content.height + self.padding
                        )
                    except AttributeError as error:
                        print(error)
                        try:
                            self._prev_content_end = (
                                self._prev_content_end + content._height + self.padding
                            )
                        except AttributeError as inner_error:
                            print(inner_error)

                else:
                    content.x = self._prev_content_end
                    if not hasattr(content, "tile_width"):
                        self._prev_content_end = (
                            content.x + content.width + (self.padding * 2)
                        )
                    else:
                        self._prev_content_end = (
                            content.x
                            + (content.width * content.tile_width)
                            + (self.padding * 2)
                        )
            else:  # use anchor point
                content.anchor_point = (
                    0,
                    content.anchor_point[1] if content.anchor_point is not None else 0,
                )
                if self.orientation == self.VERTICAL_ORIENTATION:
                    content.anchored_position = (0, self._prev_content_end)
                    # self._prev_content_end = content.y + content.height
                    if not hasattr(content, "bounding_box"):
                        self._prev_content_end = (
                            self._prev_content_end + content.height + self.padding
                        )
                    else:
                        self._prev_content_end = (
                            self._prev_content_end
                            + (content.bounding_box[3] * content.scale)
                            + self.padding
                        )

                else:
                    original_achored_pos_y = (
                        content.anchored_position[1]
                        if content.anchored_position is not None
                        else 0
                    )

                    content.anchored_position = (
                        self._prev_content_end,
                        original_achored_pos_y,
                    )
                    if not hasattr(content, "bounding_box"):
                        self._prev_content_end = (
                            self._prev_content_end + content.width + self.padding
                        )
                    else:
                        self._prev_content_end = (
                            self._prev_content_end
                            + (content.bounding_box[2] * content.scale)
                            + self.padding
                        )
