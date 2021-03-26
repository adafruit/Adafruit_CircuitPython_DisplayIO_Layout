# SPDX-FileCopyrightText: 2021 Kevin Matocha, Tim C, Jose David M
#
# SPDX-License-Identifier: MIT

"""
`adafruit_displayio_layout.widgets`
=======================
"""

import math
import vectorio

try:
    import bitmaptools
except NameError:
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
        bitmaptools.fill_region(
            bitmap, x0, y0, x0 + width - 1, y0 + height - 1, color_index
        )
    else:
        rect = vectorio.Rectangle(width, height)
        vectorio.VectorShape(
            shape=rect,
            pixel_shader=palette,
            x=x0,
            y=y0,
        )


# Created by Alexander Pletzer 2001 under the PSF license
# https://code.activestate.com/recipes/52273-colormap-returns-an-rgb-tuple-on-a-0-to-255-scale-/


def rgb(mag, cmin, cmax):
    """
    Return a tuple of integers to be used in AWT/Java plots.
    """
    red, green, blue = float_rgb(mag, cmin, cmax)
    return int(red * 255), int(green * 255), int(blue * 255)


def float_rgb(mag, cmin, cmax):
    """
    Return a tuple of floats between 0 and 1 for the red, green and
    blue amplitudes.
    """
    try:
        x = float(mag - cmin) / (cmax - cmin)
    except ZeroDivisionError:
        x = 0.5
    blue = min((max(4 * (0.75 - x), 0.0), 1.0))
    red = min((max((4 * (x - 0.25), 0.0)), 1.0))
    green = min((max((4 * math.fabs(x - 0.5) - 1.0, 0.0)), 1.0))
    return red, green, blue
