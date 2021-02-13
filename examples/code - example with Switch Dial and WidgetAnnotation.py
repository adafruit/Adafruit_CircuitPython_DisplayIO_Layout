###############
# This is a trial of the Dial and the Widget_Annotation
# for use on the PyPortal
#

import time
import board
import displayio
from adafruit_displayio_layout.widgets.switch_round import SwitchRound as Switch
from adafruit_displayio_layout.widgets.dial import Dial
from adafruit_displayio_layout.widgets.widget_annotation import WidgetAnnotation
from adafruit_bitmap_font import bitmap_font
import adafruit_touchscreen

screen_width = 320
screen_height = 240

# setup the touchscreen
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(screen_width, screen_height),
)

glyphs="0123456789"

# Font used for the Dial value indicator
font_file="fonts/DSEG7Classic-Regular-60.bdf"
my_font = bitmap_font.load_font(font_file)
                # preload the number glyphs to reduce jitter during Dial value updates
my_font.load_glyphs(glyphs)

# Font used for the Dial tick labels
font_file2="fonts/Helvetica-Bold-16.bdf"
my_font2=bitmap_font.load_font(font_file2)

# Font used for the WidgetAnnotation
font_file3="fonts/BitstreamVeraSans-Oblique-10.bdf"
annotation_font=bitmap_font.load_font(font_file3)
#annotation_font=my_font2

display = board.DISPLAY # create the display on the PyPortal,
                        # otherwise change this to setup the display
                        # for display chip driver and pinout you have (e.g. ILI9341)


# Create a Dial widget
my_dial=Dial(
    width=247,
    padding=10,
    sweep_angle=180,
    needle_width=9, # best if this is an odd number
    major_ticks=5,
    major_tick_stroke=3,
    minor_ticks=5,
    minor_tick_stroke=1,
    anchor_point=(0.5, 1),
    anchored_position=[screen_width//2, screen_height-70],
    value=0,
    value_font=my_font,
    value_color=0xBB5500,
    display_value=True,
    rotate_tick_labels=True,
    major_tick_labels=["0", '25', '50', "75", "100"],
    tick_label_scale=1.0,
    tick_label_font=my_font2,
    label_anchor_on_widget=(0.5, 0.65),
    )

# Create a Switch widget
my_switch = Switch(
    name="Annotation",
    x=screen_width//2-40,
    y=screen_height-55,
    height=50,
    display_button_text=True,
    touch_padding=10,
    value=False,
)

my_group=displayio.Group(max_size=4)
annotation_group=displayio.Group(max_size=10)

print("\n\nAbout to display...")

my_group.append(my_dial)
my_group.append(my_switch)
my_group.append(annotation_group)

annotation_color=0xBBBBBB # gray color for annotation line and text

# Add a few WidgetAnnotations on the dial
annotation = WidgetAnnotation(my_dial, text="rotate_tick_labels",
                              font=annotation_font,
                              line_color=annotation_color,
                              delta_x=-5, delta_y=-10,
                              anchor_point=(0.18, 0.33),
                              position_offset=(0,0),
                              text_offset=(20,-1),
                              )

annotation2 = WidgetAnnotation(my_dial, text="tick label",
                              font=annotation_font,
                              line_color=annotation_color,
                              delta_x=+20, delta_y=-5,
                              anchor_point=(0.8, 0.38),
                              position_offset=(5,-7),
                              text_offset=(3,-1),
                              )

annotation3 = WidgetAnnotation(my_dial, text="Origin (0,0)",
                              font=annotation_font,
                              line_color=annotation_color,
                              delta_x=+20, delta_y=-15,
                              anchored_position=(0, 0),
                              position_offset=(0,0),
                              text_offset=(3,-1),
                              )

annotation4 = WidgetAnnotation(my_dial, text="major tick",
                              font=annotation_font,
                              line_color=annotation_color,
                              delta_x=+40, delta_y=-45,
                              anchor_point=(0.51, 0.25),
                              position_offset=(0,0),
                              text_offset=(10,-1),
                              )

annotation5 = WidgetAnnotation(my_dial, text="needle",
                              font=annotation_font,
                              line_color=annotation_color,
                              delta_x=+20, delta_y=15,
                              anchored_position=(125,120),
                              position_offset=(0,0),
                              text_offset=(3,1),
                              text_under=True,
                              )

annotation6 = WidgetAnnotation(my_dial, text="minor tick",
                              font=annotation_font,
                              line_color=annotation_color,
                              delta_x=round(40*0.7), delta_y=round(-45*0.7),
                              anchor_point=(0.62,0.28),
                              position_offset=(0,0),
                              text_offset=(5,1),
                              text_under=True,
                              )

annotation7 = WidgetAnnotation(my_dial, text="value",
                              font=annotation_font,
                              line_color=annotation_color,
                              delta_x=-45, delta_y=25,
                              anchored_position=(120,105),
                              text_offset=(-1,1),
                              text_under=True,
                              )

# Add the Dial annotates to the annotation_group
annotation_group.append(annotation)
annotation_group.append(annotation2)
annotation_group.append(annotation3)
annotation_group.append(annotation4)
annotation_group.append(annotation5)
annotation_group.append(annotation6)
annotation_group.append(annotation7)

annotation_group.hidden=True # overcome a bug if you set group.hidden = True before
                             # appending group content

display.show(my_group) # add high level Group to the display
annotation_group.hidden = (not my_switch.value)
display.auto_refresh = True
display.refresh()

while True:
    # start_time=time.monotonic()

    for i in range(0,100,2):

        p = ts.touch_point
        # print("touch_point p: {}".format(p))
        if p: # if touched, check if switch was triggered
            if my_switch.contains(p):
                my_switch.selected(p)
                annotation_group.hidden = (not my_switch.value)

        display.auto_refresh=False
        my_dial.value=i
        display.auto_refresh=True
        display.refresh()
        time.sleep(0.005) # small delay seems to improve touch response

    for i in range(100,0,-8):
        p = ts.touch_point
        # print("touch_point p: {}".format(p))
        if p: # if touched, check if switch was triggered
            if my_switch.contains(p):
                my_switch.selected(p)
                annotation_group.hidden = (not my_switch.value)

        display.auto_refresh=False
        my_dial.value=i
        display.auto_refresh=True
        display.refresh()
        time.sleep(0.005) # small delay seems to improve touch response
    # end_time=time.monotonic()
    # print("One cycle: {} seconds".format(end_time-start_time))




