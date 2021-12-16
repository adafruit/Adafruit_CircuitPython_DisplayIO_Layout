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
    x=30,  # x position for the plane
    y=2,  # y plane position
    width=128,  # display width
    height=105,  # display height
    xrange=(0, 100),  # x range
    yrange=(0, 100),  # y range
)

my_group = displayio.Group()
my_group.append(my_plane)
display.show(my_group)  # add high level Group to the display

data = [
    (0, 0),
    (1, 10),
    (20, 50),
    (30, 60),
    (40, 40),
    (50, 80),
    (60, 20),
    (70, 60),
    (80, 30),
    (100, 100),
]

print("examples/displayio_layout_cartesian_lineplot.py")
for x, y in data:
    my_plane.update_line(x, y)
    time.sleep(0.5)
    print(my_plane.plot_line_point)

while True:
    pass
