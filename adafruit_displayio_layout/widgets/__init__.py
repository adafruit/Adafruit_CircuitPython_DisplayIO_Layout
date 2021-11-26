# SPDX-FileCopyrightText: 2021 Kevin Matocha, Tim C, Jose David M
#
# SPDX-License-Identifier: MIT

"""
`adafruit_displayio_layout.widgets`
=======================
"""

import vectorio

try:
    import bitmaptools
except ImportError:
    pass


# pylint: disable=invalid-name, too-many-arguments
def rectangle_helper(
    x0: int,
    y0: int,
    height: int,
    width: int,
    bitmap,
    color_index: int,
    palette,
    bitmaptool: bool = True,
) -> None:
    """rectangle_helper function
    Draws a rectangle to the bitmap given using ``bitmapstools.bitmap`` or
    ``vectorio.rectangle`` functions

    :param int x0: rectangle lower corner x position
    :param int y0: rectangle lower corner y position

    :param int width: rectangle upper corner x position
    :param int height: rectangle upper corner y position

    :param int color_index: palette color index to be used
    :param palette: palette object to be used to draw the rectangle

    :param bitmap: bitmap for the rectangle to be drawn
    :param bool bitmaptool: uses :py:func:`~bitmaptools.draw_line` to draw the rectanlge.
     when `False` uses :py:func:`~vectorio.Rectangle`

    :return: None
    :rtype: None

             ┌───────────────────────┐
             │                       │
             │                       │
     (x0,y0) └───────────────────────┘

    """
    if bitmaptool:
        bitmaptools.fill_region(bitmap, x0, y0, x0 + width, y0 + height, color_index)
    else:
        rect = vectorio.Rectangle(width, height)
        vectorio.VectorShape(
            shape=rect,
            pixel_shader=palette,
            x=x0,
            y=y0,
        )
