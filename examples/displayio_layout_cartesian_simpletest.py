# SPDX-FileCopyrightText: 2021 Jose David Montoya
#
# SPDX-License-Identifier: MIT
#############################
"""
This is a basic demonstration of a Cartesian widget.
"""

import board
import displayio
import terminalio
from adafruit_displayio_layout.widgets.cartesian import Cartesian

# Fonts used for the Dial tick labels
tick_font = terminalio.FONT

display = board.DISPLAY  # create the display on the PyPortal or Clue (for example)
# otherwise change this to setup the display
# for display chip driver and pinout you have (e.g. ILI9341)


# Create a Dial widget
my_plane = Cartesian(
    width=display.width,  # display width
    height=display.height,  # display height
    axes_color=0xFFFFFF,  # axes line color
    axes_stroke=2,  # axes lines width in pixels
    tick_color=0xFFFFFF,  # ticks color
    major_tick_stroke=1,  # ticks width in pixels
    major_tick_length=10,  # ticks length in pixels
    tick_label_color=0xFFFFFF,  # ticks line color
    tick_label_font=tick_font,  # the font used for the tick labels
)

my_group = displayio.Group(max_size=3)
my_group.append(my_plane)
display.show(my_group)  # add high level Group to the display

while True:
    pass
