# SPDX-FileCopyrightText: 2021 Jose David M.
#
# SPDX-License-Identifier: MIT
#############################
"""
This is a basic demonstration of a Slider widget.
"""

import time
import board
import displayio
import adafruit_touchscreen
from adafruit_displayio_layout.widgets.slider import Slider

display = board.DISPLAY

ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(display.width, display.height),
)

# Create the slider
my_slider = Slider(20, 30)

my_group = displayio.Group(max_size=5)
my_group.append(my_slider)

# Add my_group to the display
display.show(my_group)

# Start the main loop
while True:

    p = ts.touch_point  # get any touches on the screen

    if p:  # Check each slider if the touch point is within the slider touch area
        if my_slider.when_inside(p):
            my_slider.when_selected(p)

    time.sleep(0.05)  # touch response on PyPortal is more accurate with a small delay
