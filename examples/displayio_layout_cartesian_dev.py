# SPDX-FileCopyrightText: 2021 Stefan Krüger
#
# SPDX-License-Identifier: MIT
#############################
"""
This is a basic demonstration of a Cartesian widget for line-ploting
"""

import time
import board
import displayio
from adafruit_displayio_layout.widgets.cartesian import Cartesian

# create the display on the PyPortal or Clue or PyBadge(for example)
display = board.DISPLAY
# otherwise change this to setup the display
# for display chip driver and pinout you have (e.g. ILI9341)

# pybadge display:  160x128
# Create a Cartesian widget
# https://circuitpython.readthedocs.io/projects/displayio-layout/en/latest/api.html#module-adafruit_displayio_layout.widgets.cartesian
my_plane = Cartesian(
    x=11,  # x position for the plane
    y=0,  # y plane position
    width=140,  # display width
    height=120,  # display height
    xrange=(0, 10),  # x range
    yrange=(0, 10),  # y range
    major_tick_stroke=1,  # ticks width in pixels
    major_tick_length=2,  # ticks length in pixels
    axes_stroke=1,  # axes lines width in pixels
    axes_color=0x10A0A0,  # axes line color
    subticks=True,
)

my_group = displayio.Group()
my_group.append(my_plane)
display.show(my_group)  # add high level Group to the display

data = [
    (0, 0),
    (1, 1),
    (3, 3),
    (5, 5),
    (7, 7),
    (9, 9),
]

print("examples/displayio_layout_cartesian_lineplot.py")
for x, y in data:
    my_plane.update_line(x, y)
    # my_plane.update_pointer(x, y)
    # print(my_plane.plot_line_point)
    time.sleep(2.5)

while True:
    pass
