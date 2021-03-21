# SPDX-FileCopyrightText: Kevin Matocha
#
# SPDX-License-Identifier: MIT

"""
`adafruit_displayio_layout.widgets`
=======================
"""

import math

# * Copyright (c) 2017 Werner Stoop <wstoop@gmail.com>
# *
# * Permission is hereby granted, free of charge, to any person obtaining a copy
# * of this software and associated documentation files (the "Software"), to deal
# * in the Software without restriction, including without limitation the rights
# * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# * copies of the Software, and to permit persons to whom the Software is
# * furnished to do so, subject to the following conditions:
# *
# * The above copyright notice and this permission notice shall be included in all
# * copies or substantial portions of the Software.
# *
# * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# * SOFTWARE.


# Credit from https://github.com/wernsey/bitmap
# MIT License from
#  * Copyright (c) 2017 Werner Stoop <wstoop@gmail.com>
#
# /**
# * #### `void bm_rotate_blit(Bitmap *dst, int ox, int oy, Bitmap *src, int px,
# * int py, double angle, double scale);`
# *
# * Rotates a source bitmap `src` around a pivot point `px,py` and blits it
# * onto a destination bitmap `dst`.
# *
# * The bitmap is positioned such that the point `px,py` on the source is at
# * the offset `ox,oy` on the destination.
# *
# * The `angle` is clockwise, in radians. The bitmap is also scaled by the
# * factor `scale`.
# */
# void bm_rotate_blit(Bitmap *dst, int ox, int oy, Bitmap *src, int px,
# int py, double angle, double scale);


#     /*
#    Reference:
#    "Fast Bitmap Rotation and Scaling" By Steven Mortimer, Dr Dobbs' Journal, July 01, 2001
#    http://www.drdobbs.com/architecture-and-design/fast-bitmap-rotation-and-scaling/184416337
#    See also http://www.efg2.com/Lab/ImageProcessing/RotateScanline.htm
#    */
# This function is provided in case the bitmaptools.rotozoom function is not available

# pylint: disable=invalid-name, too-many-branches, too-many-statements, too-many-locals
# pylint: disable=too-many-arguments
def _blit_rotate_scale(
    destination,  # destination bitmap
    ox=None,
    oy=None,  # (ox, oy) is the destination point where the source (px,py) is placed
    dest_clip0=None,
    dest_clip1=None,  # clip0,1 is (x,y) corners of clip window on the destination bitmap
    source=None,  # source bitmap
    px=None,
    py=None,  # (px, py) is the rotation point of the source bitmap
    source_clip0=None,
    source_clip1=None,  # clip0,1 is (x,y) corners of clip window on the source bitmap
    angle=0,  # in radians, clockwise
    scale=1.0,  # scale factor (float)
    skip_index=None,  # color index to ignore
):

    if source is None:
        pass

    # Check the input limits

    if ox is None:
        ox = destination.width / 2
    if oy is None:
        oy = destination.height / 2
    if px is None:
        px = source.width / 2
    if py is None:
        py = source.height / 2

    if dest_clip0 is None:
        dest_clip0 = (0, 0)
    if dest_clip1 is None:
        dest_clip1 = (destination.width, destination.height)

    if source_clip0 is None:
        source_clip0 = (0, 0)
    if source_clip1 is None:
        source_clip1 = (source.width, source.height)

    minx = dest_clip1[0]
    miny = dest_clip1[1]
    maxx = dest_clip0[0]
    maxy = dest_clip0[1]

    sinAngle = math.sin(angle)
    cosAngle = math.cos(angle)

    dx = -cosAngle * px * scale + sinAngle * py * scale + ox
    dy = -sinAngle * px * scale - cosAngle * py * scale + oy
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(dy)
    dx = cosAngle * (source.width - px) * scale + sinAngle * py * scale + ox
    dy = sinAngle * (source.width - px) * scale - cosAngle * py * scale + oy
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(round(dy))

    dx = (
        cosAngle * (source.width - px) * scale
        - sinAngle * (source.height - py) * scale
        + ox
    )
    dy = (
        sinAngle * (source.width - px) * scale
        + cosAngle * (source.height - py) * scale
        + oy
    )
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(round(dy))

    dx = -cosAngle * px * scale - sinAngle * (source.height - py) * scale + ox
    dy = -sinAngle * px * scale + cosAngle * (source.height - py) * scale + oy
    if dx < minx:
        minx = int(round(dx))
    if dx > maxx:
        maxx = int(round(dx))
    if dy < miny:
        miny = int(round(dy))
    if dy > maxy:
        maxy = int(round(dy))

    # /* Clipping */
    if minx < dest_clip0[0]:
        minx = dest_clip0[0]
    if maxx > dest_clip1[0] - 1:
        maxx = dest_clip1[0] - 1
    if miny < dest_clip0[1]:
        miny = dest_clip0[1]
    if maxy > dest_clip1[1] - 1:
        maxy = dest_clip1[1] - 1

    dvCol = math.cos(angle) / scale
    duCol = math.sin(angle) / scale

    duRow = dvCol
    dvRow = -duCol

    startu = px - (ox * dvCol + oy * duCol)
    startv = py - (ox * dvRow + oy * duRow)

    rowu = startu + miny * duCol
    rowv = startv + miny * dvCol

    for y in range(miny, maxy + 1):  # (y = miny, y <= maxy, y++)
        u = rowu + minx * duRow
        v = rowv + minx * dvRow
        for x in range(minx, maxx + 1):  # (x = minx, x <= maxx, x++)
            if (source_clip0[0] <= u < source_clip1[0]) and (
                source_clip0[1] <= v < source_clip1[1]
            ):
                # get the pixel color (c) from the source bitmap at (u,v)
                c = source[
                    int(u) + source.width * int(v)
                ]  # direct index into bitmap is faster than tuple
                # c = source[int(u), int(v)]

                if c != skip_index:  # ignore any pixels with skip_index
                    # place the pixel color (c) into the destination bitmap at (x,y)
                    destination[
                        x + y * destination.width
                    ] = c  # direct index into bitmap is faster than tuple
                    # destination[x,y] = c
            u += duRow
            v += dvRow

        rowu += duCol
        rowv += dvCol
