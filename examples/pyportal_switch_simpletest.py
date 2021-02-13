<<<<<<< HEAD
=======

>>>>>>> 4dfdce6 (Initial commit with Widget, Control and WidgetLabel class definitions, includes horizontal switch widget definition and PyPortal example)
# This is a trial of the switch_round_horizontal
# for use on the PyPortal
#


import time
import board
import displayio
from adafruit_display_shapes.rect import Rect
import adafruit_touchscreen
from adafruit_pyportal import PyPortal
from adafruit_displayio_layout.widgets.switch_round import SwitchRound as Switch

display = board.DISPLAY

screen_width = 320
screen_height = 240
<<<<<<< HEAD
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(screen_width, screen_height),
)
=======
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000),
                                                   (5800, 57000)),
                                      size=(screen_width, screen_height))
>>>>>>> 4dfdce6 (Initial commit with Widget, Control and WidgetLabel class definitions, includes horizontal switch widget definition and PyPortal example)

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

<<<<<<< HEAD
switch_width = 4 * switch_radius  # This is a good aspect ratio to start with

switch_stroke = 2  # Width of the outlines (in pixels)
text_stroke = switch_stroke  # width of text lines
touch_padding = 0  # Additional boundary around widget that will accept touch input

animation_time = 0.2  # time for switch to display change (in seconds).
                      # animation_time=0.15 is a good starting point
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
    flip=True,  # Switch in the opposite direction
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
    x=switch_x + 240,
    y=switch_y,
    name="Vertical",  # include a label
    label_anchor_point=(0, 0.5),  # set the label's anchor
    label_anchor_on_widget=(1.1, 0.5),  # set the label anchor point on the widget
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
    horizontal=False,  # Use vertical orientation
    flip=True,  # flip orientation
)

# Show repositioning switch with anchor_point and anchored_position
my_switch5.anchor_point = (1, 0)
my_switch5.anchored_position = (320 - 60, 40)

my_switch6 = Switch(
    x=0,
    y=0,
    name="BIG Switch",  # include a label
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

# Show repositioning switch with anchor_point and anchored_position
my_switch6.anchor_point = (1, 1)
my_switch6.anchored_position = (305, 225)

my_group = displayio.Group(max_size=8)
=======
switch_width=4*switch_radius # This is a good aspect ratio to start with

switch_stroke = 2 # Width of the outlines (in pixels)
text_stroke = switch_stroke # width of text lines
touch_padding = 0 # Additional boundary around widget that will accept touch input

animation_time = 0.2 # time for switch to display change (in seconds).  0.15 is a good starting point
display_text = True # show the text (0/1)

# initialize state variables
switch_value=False
switch_value=True

my_switch=Switch(x=switch_x, y=switch_y,
                                height=switch_radius*2,
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
                                value=False)

my_switch2=Switch(x=switch_x+100, y=switch_y,
                                height=switch_radius*2,
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
                                value=False)

my_switch3=Switch(x=switch_x, y=switch_y+55,
                                height=switch_radius*2,
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
                                value=False)

my_switch4=Switch(x=switch_x+100, y=switch_y+55,
                                height=switch_radius*2,
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
                                value=False)

my_switch5=Switch(x=0, y=0,
                  name="BIG Switch",
                                height=switch_radius*4,
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
                                animation_time=0.3, # for larger button, may want to extend the animation time
                                text_stroke=6, ## Add a wider text stroke
                                value=False)

my_switch5.anchor_point=(1,1)
my_switch5.anchored_position=(305, 225)

my_group=displayio.Group(max_size=8)
>>>>>>> 4dfdce6 (Initial commit with Widget, Control and WidgetLabel class definitions, includes horizontal switch widget definition and PyPortal example)

my_group.append(my_switch)
my_group.append(my_switch2)
my_group.append(my_switch3)
my_group.append(my_switch4)
my_group.append(my_switch5)
my_group.append(my_switch6)

# Add my_group to the display
display.show(my_group)

display.refresh(target_frames_per_second=60, minimum_frames_per_second=30)

# Start the main loop
while True:

    p = ts.touch_point
<<<<<<< HEAD
    # print("touch_point p: {}".format(p))
=======
    #print("touch_point p: {}".format(p))
>>>>>>> 4dfdce6 (Initial commit with Widget, Control and WidgetLabel class definitions, includes horizontal switch widget definition and PyPortal example)

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

<<<<<<< HEAD:examples/pyportal_switch_simpletest.py
        elif my_switch6.contains(p):
            my_switch6.selected(p)

=======
<<<<<<< HEAD
>>>>>>> main:examples/pyportal_horizontal_switch_simpletest.py
    time.sleep(0.05)  # touch response on PyPortal is more accurate with a small delay
=======
    time.sleep(0.05) # touch response on PyPortal is more accurate with a small delay
>>>>>>> 4dfdce6 (Initial commit with Widget, Control and WidgetLabel class definitions, includes horizontal switch widget definition and PyPortal example)
