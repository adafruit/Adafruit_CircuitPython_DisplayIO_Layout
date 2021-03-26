# SPDX-FileCopyrightText: 2021 Jose David M.
#
# SPDX-License-Identifier: MIT
#############################
"""
This is a basic demonstration of a Equalizer widget.
"""

import time
import board
import displayio
from adafruit_displayio_layout.widgets.equalizer import Equalizer

display = board.DISPLAY  # create the display on the PyPortal or Clue (for example)
# otherwise change this to setup the display
# for display chip driver and pinout you have (e.g. ILI9341)


# Create a Equalizer widget
my_equa = Equalizer(
    x=100,
    y=100,
    width=100,
    height=100,
    number_bars=5,
    bar_width=10,
    number_segments=6,
    segments_height=25,
    bar_best_fit=True,
    pad_x=2,
)

my_group = displayio.Group(max_size=3)
my_group.append(my_equa)
display.show(my_group)  # add high level Group to the display

while True:
    # We updates the values for 5 bars. We update the values for
    # each bar
    my_equa.show_bars((10, 0, 10, 35, 85))
    time.sleep(0.5)

    my_equa.show_bars((70, 10, 0, 10, 35))
    time.sleep(0.5)

    my_equa.show_bars((0, 10, 35, 0, 90))
    time.sleep(0.5)

    my_equa.show_bars((35, 85, 10, 0, 10))
    time.sleep(0.5)

    my_equa.show_bars((10, 35, 85, 10, 0))
    time.sleep(0.5)

    my_equa.show_bars((0, 10, 35, 56, 90))
    time.sleep(0.5)
