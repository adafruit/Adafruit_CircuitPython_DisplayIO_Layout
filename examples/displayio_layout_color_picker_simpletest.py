# SPDX-FileCopyrightText: 2021 Jose David
#
# SPDX-License-Identifier: MIT
"""
Creates a single color picker
"""

import time
import board
import terminalio
from displayio import Group, TileGrid, Bitmap, Palette
from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.widgets.color_picker import ColorPicker
import adafruit_touchscreen


display = board.DISPLAY

# TouchScreen Configuration
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(display.width, display.height),
)

# Colorwheel Bitmap file
filename = "wheel200.bmp"  # You can find this file in the examples directory in the library Github
# Change the imagesize_used according to the bitmap file used. Colorwheel are identified
# according to the size in pixels
imagesize_used = 200
my_colorpicker = ColorPicker(
    filename,
    display.width // 2 - imagesize_used // 2,
    display.height // 2 - imagesize_used // 2,
    imagesize_used,
)
my_group = Group(max_size=4)
my_group.append(my_colorpicker)

palette = Palette(2)
palette[0] = 0x990099
palette[1] = 0x00FFFF

bitmap = Bitmap(100, 20, 2)
color_square = TileGrid(bitmap, pixel_shader=palette, x=display.width - 100, y=10)
my_group.append(color_square)
# Adding text information
text_area = bitmap_label.Label(
    terminalio.FONT,
    text="Color",
    x=display.width - 100,
    y=35,
)
my_group.append(text_area)

# Add my_group to the display
display.show(my_group)

p = False
# Start the main loop
while True:
    p = ts.touch_point
    if p:  # Check if colorpicker is selected
        if my_colorpicker.contains(p):
            color = my_colorpicker.when_selected(p, display.height)
            palette[0] = color
            print(f"Color Selected is: {hex(color)}")
            text_area.text = str(hex(color))
            time.sleep(1.5)

    time.sleep(0.05)  # touch response on PyPortal is more accurate with a small delay
