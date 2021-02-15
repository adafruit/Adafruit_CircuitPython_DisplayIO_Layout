###############
# This is a trial of the Dial and the Widget_Annotation
# for use on the PyPortal
#

import time
import board
import displayio
from adafruit_displayio_layout.widgets.flip_input import FlipInput

from adafruit_bitmap_font import bitmap_font
import adafruit_touchscreen

display = board.DISPLAY  # create the display on the PyPortal,
# otherwise change this to setup the display
# for display chip driver and pinout you have (e.g. ILI9341)

# setup the touchscreen
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(display.width, display.height),
)

# Select the font file for use
font_file = "fonts/DSEG14Classic-Regular-64-ModS.bdf"
my_font = bitmap_font.load_font(font_file)

my_flip1 = FlipInput(
    anchor_point=[0.0, 0.0],
    anchored_position=[10, 40],
    color=0xFF2222,
    value_list=[
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ],
    font=my_font,
    arrow_touch_padding=40,
    arrow_color=0x333333,
    arrow_outline=0x444444,
    arrow_height=20,
    arrow_width=30,
    horizontal=False,
)

my_flip2 = FlipInput(
    anchor_point=[0.0, 0.0],
    anchored_position=[180, 40],
    color=0xFF2222,
    value_list=["{0:02d}".format(x) for x in range(1, 31 + 1)],
    font=my_font,
    arrow_touch_padding=40,
    arrow_color=0x333333,
    arrow_outline=0x444444,
    arrow_height=20,
    arrow_width=30,
    horizontal=False,
)

my_flip3 = FlipInput(
    anchor_point=[0.5, 1.0],
    anchored_position=[320 // 2, 240 - 10],
    color=0xFF2222,
    value_list=["{0:02d}".format(x) for x in range(1985, 2022, 1)],
    font=my_font,
    arrow_touch_padding=40,
    arrow_color=0x333333,
    arrow_outline=0x444444,
    arrow_height=30,
    arrow_width=20,
    horizontal=True,
)

my_flip1.value = my_flip1.value_list.index("OCT")
my_flip2.value = my_flip2.value_list.index("15")
my_flip3.value = my_flip3.value_list.index("2015")

# Create the group to display and append the FlipInput widgets
my_group = displayio.Group(max_size=3)
my_group.append(my_flip1)
my_group.append(my_flip2)
my_group.append(my_flip3)

display.show(my_group)  # add high level Group to the display
display.auto_refresh = True

while True:

    p = ts.touch_point
    # print("touch_point p: {}".format(p)) # print the touch point

    if p:  # if touched, check if any of the widgets was triggered
        if my_flip1.contains(p):
            my_flip1.selected(p)
            time.sleep(0.15)  # add a short delay to reduce accidental press
        elif my_flip2.contains(p):
            my_flip2.selected(p)
            time.sleep(0.15)  # add a short delay to reduce accidental press
        elif my_flip3.contains(p):
            my_flip3.selected(p)
            time.sleep(0.15)  # add a short delay to reduce accidental press

    time.sleep(0.01)  # small delay seems to improve touch response
