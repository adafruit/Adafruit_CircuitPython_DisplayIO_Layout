# This is a trial of the switch_round_horizontal
# for use on the PyPortal
#


import time
import board
import displayio
from adafruit_display_shapes.rect import Rect
from switch_round_horizontal import SwitchRoundHorizontal as Switch

import adafruit_touchscreen
from adafruit_pyportal import PyPortal

display = board.DISPLAY

screen_width = 320
screen_height = 240
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(screen_width, screen_height),
)

switch_x = 30
switch_y = 30
switch_radius = 20

switch_fill_color_off = (66, 44, 66)
switch_fill_color_on = (0, 100, 0)

switch_outline_color_off = (30, 30, 30)
switch_outline_color_on = (0, 60, 0)

background_color_off = (255, 255, 255)
background_color_on = (90, 255, 90)

background_outline_color_off = background_color_off
background_outline_color_on = background_color_on

switch_width = 4 * switch_radius  # This is a good aspect ratio to start with

switch_stroke = 2  # Width of the outlines (in pixels)
text_stroke = switch_stroke  # width of text lines
touch_padding = 0  # Additional boundary around widget that will accept touch input

animation_time = 0.2  # time for switch to display change (in seconds).  0.15 is a good starting point
display_text = True  # show the text (0/1)

# initialize state variables
switch_value = False
switch_value = True

my_switch = Switch(
    x=switch_x,
    y=switch_y,
    height=switch_radius * 2,
    fill_color_off=switch_fill_color_off,
    fill_color_on=switch_fill_color_on,
    outline_color_off=switch_outline_color_off,
    outline_color_on=switch_outline_color_on,
    background_color_off=background_color_off,
    background_color_on=background_color_on,
    background_outline_color_off=background_outline_color_off,
    background_outline_color_on=background_outline_color_on,
    switch_stroke=switch_stroke,
    display_button_text=display_text,
    touch_padding=10,
    animation_time=animation_time,
    value=False,
)

my_switch2 = Switch(
    x=switch_x + 100,
    y=switch_y,
    height=switch_radius * 2,
    fill_color_off=switch_fill_color_off,
    fill_color_on=switch_fill_color_on,
    outline_color_off=switch_outline_color_off,
    outline_color_on=switch_outline_color_on,
    background_color_off=background_color_off,
    background_color_on=background_color_on,
    background_outline_color_off=background_outline_color_off,
    background_outline_color_on=background_outline_color_on,
    switch_stroke=switch_stroke,
    display_button_text=False,
    touch_padding=touch_padding,
    animation_time=animation_time,
    value=False,
)

my_switch3 = Switch(
    x=switch_x,
    y=switch_y + 55,
    height=switch_radius * 2,
    fill_color_off=(255, 0, 0),
    fill_color_on=switch_fill_color_on,
    outline_color_off=(80, 0, 0),
    outline_color_on=switch_outline_color_on,
    background_color_off=(150, 0, 0),
    background_color_on=background_color_on,
    background_outline_color_off=(30, 0, 0),
    background_outline_color_on=background_outline_color_on,
    switch_stroke=switch_stroke,
    display_button_text=True,
    touch_padding=touch_padding,
    animation_time=animation_time,
    value=False,
)

my_switch4 = Switch(
    x=switch_x + 100,
    y=switch_y + 55,
    height=switch_radius * 2,
    fill_color_off=(255, 0, 0),
    fill_color_on=switch_fill_color_on,
    outline_color_off=(80, 0, 0),
    outline_color_on=switch_outline_color_on,
    background_color_off=(150, 0, 0),
    background_color_on=background_color_on,
    background_outline_color_off=(30, 0, 0),
    background_outline_color_on=background_outline_color_on,
    switch_stroke=switch_stroke,
    display_button_text=False,
    touch_padding=touch_padding,
    animation_time=animation_time,
    value=False,
)

my_switch5 = Switch(
    x=0,
    y=0,
    name="BIG Switch",
    height=switch_radius * 4,
    fill_color_off=switch_fill_color_off,
    fill_color_on=switch_fill_color_on,
    outline_color_off=switch_outline_color_off,
    outline_color_on=switch_outline_color_on,
    background_color_off=background_color_off,
    background_color_on=background_color_on,
    background_outline_color_off=background_outline_color_off,
    background_outline_color_on=background_outline_color_on,
    switch_stroke=switch_stroke,
    display_button_text=True,
    touch_padding=10,
    animation_time=0.3,  # for larger button, may want to extend the animation time
    text_stroke=6,  ## Add a wider text stroke
    value=False,
)

my_switch5.anchor_point = (1, 1)
my_switch5.anchored_position = (305, 225)

my_group = displayio.Group(max_size=8)

my_group.append(my_switch)
my_group.append(my_switch2)
my_group.append(my_switch3)
my_group.append(my_switch4)
my_group.append(my_switch5)

# Add my_group to the display
display.show(my_group)

display.refresh(target_frames_per_second=60, minimum_frames_per_second=30)

# Start the main loop
while True:

    p = ts.touch_point
    # print("touch_point p: {}".format(p))

    if p:
        if my_switch.contains(p):
            my_switch.selected(p)

        elif my_switch2.contains(p):
            my_switch2.selected(p)
        elif my_switch3.contains(p):
            my_switch3.selected(p)
        elif my_switch4.contains(p):
            my_switch4.selected(p)
        elif my_switch5.contains(p):
            my_switch5.selected(p)

    time.sleep(0.05)  # touch response on PyPortal is more accurate with a small delay
