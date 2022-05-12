# SPDX-FileCopyrightText: 2022 PaulskPt
#
# SPDX-License-Identifier: MIT
"""
Make a PageLayout and illustrate all of it's features
"""
# pylint: disable-all
import time
import displayio
import board
import terminalio
import adafruit_tmp117
from adafruit_ds3231 import DS3231
from adafruit_display_text.bitmap_label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.triangle import Triangle

# from adafruit_bitmap_font import bitmap_font
from adafruit_displayio_layout.layouts.tab_layout import TabLayout

# Adjust here the date and time that you want the RTC to be set at start:
default_dt = time.struct_time((2022, 5, 2, 2, 48, 0, 0, -1, -1))

my_debug = True

months = {
    0: "Dum",
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

use_txt_in_month = True
use_usa_notation = True
use_ntp = False

i2c = board.I2C()

if my_debug:
    while not i2c.try_lock():
        pass

    try:
        while True:
            print(
                "I2C addresses found:",
                [hex(device_address) for device_address in i2c.scan()],
            )
            time.sleep(2)
            break

    finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
        i2c.unlock()


lStart = True
rtc_present = None
rtc = None
o_secs = 0  # old seconds
c_secs = 0  # current seconds

# used to flag when more or less static elements in datetime stamp have to be refreshed
dt_refresh = True

sDT_old = ""

t_sensor_present = None
tmp117 = None
t0 = None
t1 = None
t2 = None

# degs_sign = chr(186)  # I preferred the real degrees sign which is: chr(176)

content_sensor_idx = None
pge3_lbl_dflt = "The third page is fun!"
pge4_lbl_dflt = "The fourth page is where it's at"

online_time_present = None

# -----------------------------------

# built-in display
display = board.DISPLAY
# display.rotation = 90
display.rotation = 0

# create and show main_group
main_group = displayio.Group()
display.show(main_group)

# font = bitmap_font.load_font("fonts/Helvetica-Bold-16.bdf")
font = terminalio.FONT

# create the page layout
test_page_layout = TabLayout(
    x=0,
    y=0,
    display=board.DISPLAY,
    tab_text_scale=2,
    custom_font=font,
    inactive_tab_spritesheet="bmps/inactive_tab_sprite.bmp",
    showing_tab_spritesheet="bmps/active_tab_sprite.bmp",
    showing_tab_text_color=0x00AA59,
    inactive_tab_text_color=0xEEEEEE,
    inactive_tab_transparent_indexes=(0, 1),
    showing_tab_transparent_indexes=(0, 1),
    tab_count=4,
)

# make 3 pages of content
pge1_group = displayio.Group()
pge2_group = displayio.Group()
pge3_group = displayio.Group()
pge4_group = displayio.Group()

# labels
pge1_lbl = Label(
    font=terminalio.FONT,
    scale=2,
    text="This is the first page!",
    anchor_point=(0, 0),
    anchored_position=(10, 10),
)
pge1_lbl2 = Label(
    font=terminalio.FONT,
    scale=2,
    text="Please wait...",
    anchor_point=(0, 0),
    anchored_position=(10, 150),
)
pge2_lbl = Label(
    font=terminalio.FONT,
    scale=2,
    text="This page is the second page!",
    anchor_point=(0, 0),
    anchored_position=(10, 10),
)
pge3_lbl = Label(
    font=terminalio.FONT,
    scale=2,
    text=pge3_lbl_dflt,  # Will be "Date/time:"
    anchor_point=(0, 0),
    anchored_position=(10, 10),
)
pge3_lbl2 = Label(
    font=terminalio.FONT,
    scale=2,
    text="",  # pge3_lbl2_dflt,   # Will be DD-MO-YYYY or Month-DD-YYYY
    anchor_point=(0, 0),
    anchored_position=(10, 40),
)
pge3_lbl3 = Label(
    font=terminalio.FONT,
    scale=2,
    text="",  # pge3_lbl3_dflt,  # Will be HH:MM:SS
    anchor_point=(0, 0),
    anchored_position=(10, 70),
)
pge4_lbl = Label(
    font=terminalio.FONT,
    scale=2,
    text=pge4_lbl_dflt,
    anchor_point=(0, 0),
    anchored_position=(10, 10),
)
pge4_lbl2 = Label(
    font=terminalio.FONT,
    scale=2,
    text="",  # Will be "Temperature"
    anchor_point=(0, 0),
    anchored_position=(10, 130),
)
pge4_lbl3 = Label(
    font=terminalio.FONT,
    scale=2,
    text="",  # Will be  "xx.yy C"
    anchor_point=(0, 0),
    anchored_position=(10, 160),
)

# shapes
square = Rect(x=20, y=70, width=40, height=40, fill=0x00DD00)
circle = Circle(50, 100, r=30, fill=0xDD00DD)
triangle = Triangle(50, 0, 100, 50, 0, 50, fill=0xDDDD00)
rectangle = Rect(x=80, y=60, width=100, height=50, fill=0x0000DD)

triangle.x = 80
triangle.y = 70

# add everything to their page groups
pge1_group.append(square)
pge1_group.append(pge1_lbl)
pge2_group.append(pge2_lbl)
pge2_group.append(circle)
pge3_group.append(pge3_lbl)
pge3_group.append(pge3_lbl2)
pge3_group.append(pge3_lbl3)
pge3_group.append(triangle)
pge4_group.append(pge4_lbl)
pge4_group.append(pge4_lbl2)
pge4_group.append(pge4_lbl3)
pge4_group.append(rectangle)

if board.board_id == "pyportal_titano":
    pages = {0: "Dum", 1: "One", 2: "Two", 3: "Three", 4: "Four"}
else:
    pages = {0: "Dum", 1: "One", 2: "Two", 3: "Thr", 3: "For"}

# add the pages to the layout, supply your own page names
test_page_layout.add_content(pge1_group, pages[0])
test_page_layout.add_content(pge2_group, pages[1])
test_page_layout.add_content(pge3_group, pages[2])
test_page_layout.add_content(pge4_group, pages[3])

# test_page_layout.add_content(displayio.Group(), "page_5")

# add it to the group that is showing on the display
main_group.append(test_page_layout)

# test_page_layout.tab_tilegrids_group[3].x += 50

# change page with function by name
test_page_layout.show_page(page_name=pages[2])
print("showing page index:{}".format(test_page_layout.showing_page_index))
time.sleep(1)

# change page with function by index
test_page_layout.show_page(page_index=0)
print("showing page name: {}".format(test_page_layout.showing_page_name))
time.sleep(1)

# change page by updating the page name property
test_page_layout.showing_page_name = pages[2]
print("showing page index: {}".format(test_page_layout.showing_page_index))
time.sleep(1)

# change page by updating the page index property
test_page_layout.showing_page_index = 1
print("showing page name: {}".format(test_page_layout.showing_page_name))
time.sleep(5)

"""
another_text = Label(terminalio.FONT, text="And another thing!", \
    scale=2, color=0x00ff00, anchor_point=(0, 0), \
    anchored_position=(100, 100))
test_page_layout.showing_page_content.append(another_text)
"""
print("starting loop")

old_temp = 0.00

"""
  If the temperature sensor has been disconnected,
  this function will try to reconnect (test if the sensor is present by now)
  If reconnected this function sets the global variable t_sensor_present
  If failed to reconnect the function clears t_sensor_present
"""


def connect_temp_sensor():
    global t_sensor_present, tmp117, t0, t1, t2
    t = "temperature sensor found"
    t_sensor_present = False
    tmp117 = None

    try:
        tmp117 = adafruit_tmp117.TMP117(i2c)
    except ValueError:  # ValueError occurs if the temperature sensor is not connected
        pass

    if tmp117 is not None:
        t_sensor_present = True

    if t_sensor_present:
        print(t)
        print("temperature sensor connected")
        t0 = "Temperature"
        t1 = " C"
        t2 = 27 * "_"
    else:
        print("no " + t)
        print("failed to connect temperature sensor")
        t0 = None
        t1 = None
        t2 = None


"""
  If the external rtc has been disconnected,
  this function will try to reconnect (test if the external rtc is present by now)
  If reconnected this function sets the global variable rtc_present
  If failed to reconnect the function clears rtc_present
"""


def connect_rtc():
    global rtc_present, rtc, lStart
    t = "RTC found"
    rtc_present = False
    rtc = None
    try:
        rtc = DS3231(i2c)  # i2c addres 0x68
    except ValueError:
        pass

    if rtc is not None:
        rtc_present = True
        print(t)
        print("RTC connected")
        if lStart:
            lStart = False
            rtc.datetime = default_dt
    else:
        print("no " + t)
        print("Failed to connect RTC")


temp_in_REPL = False
"""
   Function gets a value from the external temperature sensor
   It only updates if the value has changed compared to the previous value
   If no value obtained (for instance if the sensor is disconnected)
   the function sets the page_4 label to a default text
"""


def get_temp():
    global t_sensor_present, old_temp, tmp117, pge4_lbl, pge4_lbl2, pge4_lbl3, temp_in_REPL
    showing_page_idx = test_page_layout.showing_page_index
    RetVal = False
    if t_sensor_present:
        try:
            temp = tmp117.temperature
            t = "{:5.2f} ".format(temp) + t1
            if my_debug and temp is not None and not temp_in_REPL:
                temp_in_REPL = True
                print("get_temp(): {} {}".format(t0, t))
            if showing_page_idx == 3:  # show temperature on most right Tab page
                if temp is not None:
                    if (
                        temp != old_temp
                    ):  # Only update if there is a change in temperature
                        old_temp = temp
                        t = "{:5.2f} ".format(temp) + t1
                        pge4_lbl.text = ""
                        pge4_lbl2.text = t0
                        pge4_lbl3.text = t
                        # if not my_debug:
                        # print("pge4_lbl.text = {}".format(pge4_lbl.text))
                        # time.sleep(2)
                        RetVal = True
                else:
                    t = ""
                    pge4_lbl.text = pge4_lbl_dflt
        except OSError:
            print("Temperature sensor has disconnected")
            t = ""
            t_sensor_present = False
            tmp117 = None
            pge4_lbl.text = pge4_lbl_dflt  # clean the line  (eventually: t2)
            pge4_lbl2.text = ""
            pge4_lbl3.text = ""

    return RetVal


yy = 0
mo = 1
dd = 2
hh = 3
mm = 4
ss = 5


"""
    Function called by get_dt()
    Created to repair pylint error R0912: Too many branches (13/12)
"""


def handle_dt(dt):
    global pge3_lbl, pge3_lbl2, pge3_lbl3, o_secs, c_secs, dt_refresh, sDT_old
    RetVal = False
    s = "Date/time: "
    sYY = str(dt[yy])
    sMO = (
        months[dt[mo]]
        if use_txt_in_month
        else "0" + str(dt[mo])
        if dt[mo] < 10
        else str(dt[mo])
    )

    dt_dict = {}

    for _ in range(dd, ss + 1):
        dt_dict[_] = "0" + str(dt[_]) if dt[_] < 10 else str(dt[_])

    if my_debug:
        print("dt_dict = ", dt_dict)

    c_secs = dt_dict[ss]
    sDT = (
        sMO + "-" + dt_dict[dd] + "-" + sYY
        if use_usa_notation
        else sYY + "-" + sMO + "-" + dt_dict[dd]
    )

    if sDT_old != sDT:
        sDT_old = sDT
        dt_refresh = True  # The date has changed, set the refresh flag
    sDT2 = dt_dict[hh] + ":" + dt_dict[mm] + ":" + dt_dict[ss]

    if dt_refresh:  # only refresh when needed
        dt_refresh = False
        pge3_lbl.text = s
        pge3_lbl2.text = sDT

    if c_secs != o_secs:
        o_secs = c_secs
        sDT3 = s + "{} {}".format(sDT, sDT2)
        print(sDT3)

        pge3_lbl3.text = sDT2
        if my_debug:
            print("pge3_lbl.text = {}".format(pge3_lbl.text))
            print("pge3_lbl2.text = {}".format(pge3_lbl2.text))
            print("pge3_lbl3.text = {}".format(pge3_lbl3.text))
        RetVal = True

    # Return from here with a False but don't set the pge3_lbl to default.
    # It is only to say to the loop() that we did't update the datetime
    return RetVal


"""
   Function gets the date and time:
   a) if an rtc is present from the rtc;
   b) if using online NTP pool server then get the date and time from the function time.localtime
   This time.localtime has before been set with data from the NTP server.
   In both cases the date and time will be set to the page3_lbl, lbl12 and lbl3
   If no (valid) date and time has been received then a default text will be shown on the page3_lbl
"""


def get_dt():
    global rtc_present, pge3_lbl, pge3_lbl2, pge3_lbl3
    dt = None
    RetVal = False

    if rtc_present:
        try:
            dt = rtc.datetime
        except OSError as exc:
            if my_debug:
                print("Error number: ", exc.args[0])
            if exc.args[0] == 5:  # Input/output error
                rtc_present = False
                print("get_dt(): OSError occurred. RTC probably is disconnected")
                pge3_lbl.text = pge3_lbl_dflt
                return RetVal
            raise  # Handle other errors

    elif online_time_present or use_ntp:
        dt = time.localtime()

    if dt is not None:
        RetVal = handle_dt(dt)
    else:
        pge3_lbl.text = pge3_lbl_dflt
        pge3_lbl2.text = ""
        pge3_lbl3.text = ""
    return RetVal


def main():
    cnt = 0
    while True:
        try:
            print("Loop nr: {:03d}".format(cnt))

            if rtc_present:
                get_dt()
            else:
                connect_rtc()

            if t_sensor_present:
                get_temp()
            else:
                connect_temp_sensor()

            cnt += 1
            if cnt > 999:
                cnt = 0
            # change page by next page function. It will loop by default
            time.sleep(2)
            test_page_layout.next_page()
        except KeyboardInterrupt as exc:
            raise KeyboardInterrupt("Keyboard interrupt...exiting...") from exc
            # raise SystemExit


if __name__ == "__main__":

    main()
