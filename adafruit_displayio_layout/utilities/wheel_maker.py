# SPDY-FileCopyrightText: 2012 jacksongabbard
# SPDX-FileCopyrightText: 2019 Dave Astels for Adafruit Industries
# SPDX-FileCopyrightText: 2021 Kevin Matocha, Jose David M.
#
# SPDX-License-Identifier: MIT
# SPDY-License-Identifier: Unlicense

"""
`adafruit_wheel_maker`
================================================================================

Save a displayio.Bitmap (and associated displayio.Palette) in a BMP file.
This script is adapted in the works from Dave Astels on the ``adafruit_bitmapsaver``
and the works of  Jackson Glabbard
https://jg.gg/2012/05/28/generating-a-color-picker-style-color-wheel-in-python/
https://github.com/jacksongabbard/Python-Color-Gamut-Generator/blob/master/color-wheel-generator.py
and Kevin Matocha on the ``switch_round`` for the ``_color_to_tuple`` function

* Author(s): Dave Astels, Jackson Glabbard, Kevin Matocha, Jose David M.

Implementation Notes
--------------------

**Hardware:**


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

import math
import struct
import gc
import board
import digitalio
import busio

try:
    import adafruit_sdcard
    import storage
except ImportError:
    pass

# pylint: disable=invalid-name, no-member, too-many-locals


def _write_bmp_header(output_file, filesize):
    output_file.write(bytes("BM", "ascii"))
    output_file.write(struct.pack("<I", filesize))
    output_file.write(b"\00\x00")
    output_file.write(b"\00\x00")
    output_file.write(struct.pack("<I", 54))


def _bytes_per_row(source_width):
    pixel_bytes = 3 * source_width
    padding_bytes = (4 - (pixel_bytes % 4)) % 4
    return pixel_bytes + padding_bytes


def _write_dib_header(output_file, width, height):
    output_file.write(struct.pack("<I", 40))
    output_file.write(struct.pack("<I", width))
    output_file.write(struct.pack("<I", height))
    output_file.write(struct.pack("<H", 1))
    output_file.write(struct.pack("<H", 24))
    for _ in range(24):
        output_file.write(b"\x00")


def make_color(base, adj, ratio, shade):
    """
    Go through each bit of the colors adjusting blue with blue, red with red,
    green with green, etc.
    """
    output = 0x0
    bit = 0
    for pos in range(3):
        base_chan = color_wheel[base][pos]
        adj_chan = color_wheel[adj][pos]
        new_chan = int(round(base_chan * (1 - ratio) + adj_chan * ratio))

        # now alter the channel by the shade
        if shade < 1:
            new_chan = new_chan * shade
        elif shade > 1:
            shade_ratio = shade - 1
            new_chan = (0xFF * shade_ratio) + (new_chan * (1 - shade_ratio))

        output = output + (int(new_chan) << bit)
        bit = bit + 8
    return output


def color_to_tuple(value):
    """Converts a color from a 24-bit integer to a tuple.
    :param value: RGB LED desired value - can be a RGB tuple or a 24-bit integer.
    """
    if isinstance(value, tuple):
        return value
    if isinstance(value, int):
        if value >> 24:
            raise ValueError("Only bits 0->23 valid for integer input")
        r = value >> 16
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return [r, g, b]

    raise ValueError("Color must be a tuple or 24-bit integer value.")


color_wheel = [
    [0xFF, 0x00, 0xFF],
    [0xFF, 0x00, 0x00],
    [0xFF, 0xFF, 0x00],
    [0x00, 0xFF, 0x00],
    [0x00, 0xFF, 0xFF],
    [0x00, 0x00, 0xFF],
    [0xFF, 0x00, 0xFF],
]


def make_wheel(image_name, img_size, bg_color):
    """
    :param image_name: TBD
    :param img_size: TBD
    :param bg_color: TBD
    :return: color
    """
    img_size_width = img_size
    img_size_height = img_size
    img_half = img_size / 2
    outer_radius = img_size // 2
    background_color = color_to_tuple(bg_color)
    row_buffer = bytearray(_bytes_per_row(img_size_width))
    result_buffer = bytearray(2048)

    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.SD_CS)
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    file_path = "/sd" + image_name
    print("saving starts")
    output_file = open(file_path, "wb")
    filesize = 54 + img_size_height * _bytes_per_row(img_size_width)
    _write_bmp_header(output_file, filesize)
    _write_dib_header(output_file, img_size_width, img_size_height)

    for y in range(img_size, 0, -1):
        buffer_index = 0
        for x in range(img_size):
            dist = abs(math.sqrt((x - img_half) ** 2 + (y - img_half) ** 2))
            shade = 1 * dist / outer_radius
            if x - img_half == 0:
                angle = -90
                if y > img_half:
                    angle = 90
            else:
                angle = math.atan2((y - img_half), (x - img_half)) * 180 / math.pi

            angle = (angle - 30) % 360

            idx = angle / 60
            if idx < 0:
                idx = 6 + idx
            base = int(round(idx))

            adj = (6 + base + (-1 if base > idx else 1)) % 6
            ratio = max(idx, base) - min(idx, base)
            color = make_color(base, adj, ratio, shade)

            if dist > outer_radius:
                color_rgb = background_color
            else:
                color_rgb = color_to_tuple(color)

            for b in color_rgb:
                row_buffer[buffer_index] = b & 0xFF
                buffer_index += 1
        output_file.write(row_buffer)
        for i in range(img_size_width * 2):
            result_buffer[i] = 0
        gc.collect()

    output_file.close()
    print("saving done")
