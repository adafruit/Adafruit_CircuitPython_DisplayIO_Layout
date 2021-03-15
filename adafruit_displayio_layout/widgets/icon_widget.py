# SPDX-FileCopyrightText: 2021 Tim Cocks
#
# SPDX-License-Identifier: MIT
"""

`icon_widget`
================================================================================
A touch enabled widget that includes an icon image with a small text label
centered below it.

* Author(s): Tim Cocks

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import gc
import time
import terminalio
import bitmaptools
from displayio import TileGrid, Bitmap, Palette
import adafruit_imageload
from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.widgets.control import Control
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.easing import quadratic_easeout as easein
from adafruit_displayio_layout.widgets.easing import quadratic_easein as easeout


class IconWidget(Widget, Control):

    """
    A touch enabled widget that holds an icon image loaded with
    adafruit_imageload and a text label centered beneath it. Includes optional
    animation to increase the icon size when pressed.

    :param string label_text: the text that will be shown beneath the icon image.
    :param string icon: the filepath of the bmp image to be used as the icon.

    :param float max_scale: the maximum zoom during animation, set 1.0 for no animation
     a value of 1.4 is a good starting point (default: 1.0, no animation),
     ``max_scale`` must be >= 1.0
    :param float max_angle: the maximum degrees of rotation during animation, set 0 for
     no rotation, in degrees (default: 0 degrees)
    :param float animation_time: the time for the animation in seconds, set to 0.0 for
     no animation, a value of 0.15 is a good starting point (default: 0.15 seconds)

    :param int x: x location the icon widget should be placed. Pixel coordinates.
    :param int y: y location the icon widget should be placed. Pixel coordinates.
    :param anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor point relative to the
     widget bounding box
    :type anchor_point: Tuple[float,float]
    :param int anchored_position: (x,y) pixel value for the location of the anchor_point
    :type anchored_position: Tuple[int, int]
    :param int max_size: (Optional) this will get passed through to the
     displayio.Group constructor. If omitted we default to
     grid_size width * grid_size height to make room for all (1, 1) sized cells.

    """

    # pylint: disable=bad-super-call, too-many-instance-attributes
    # pylint: disable=too-many-arguments, unused-argument

    def __init__(
        self,
        display,
        label_text,
        icon,
        max_scale=1.0,
        max_angle=8,
        animation_time=0.0,
        **kwargs
    ):

        super().__init__(**kwargs)  # initialize superclasses
        super(Control, self).__init__()

        self.display = display

        self._image, self._palette = adafruit_imageload.load(icon)
        tile_grid = TileGrid(self._image, pixel_shader=self._palette)
        self.append(tile_grid)
        _label = bitmap_label.Label(
            terminalio.FONT,
            scale=1,
            text=label_text,
            anchor_point=(0.5, 0),
            anchored_position=(self._image.width // 2, self._image.height),
        )
        self.append(_label)
        self.touch_boundary = (
            self.x,
            self.y,
            self._image.width,
            self._image.height + _label.bounding_box[3],
        )

        # verify the animation settings
        self._start_scale = 1.0

        max_scale = max(1.0, max_scale)  # constrain to > 1.0
        if max_scale == 1.0:  # no animation
            self._animation_time = 0
        else:
            self._animation_time = animation_time  # in seconds
        self._end_scale = max_scale

        self._angle = (max_angle / 360) * 2 * 3.14  # 5 degrees, convert to radians

        # define zoom attributes
        self._zoom_color_depth = None
        self._zoom_palette = None
        self._zoom_bitmap = None
        self._zoom_tilegrid = None

        self.value = False  # initial value

    def contains(self, touch_point):  # overrides, then calls Control.contains(x,y)

        """Checks if the IconWidget was touched.  Returns True if the touch_point is
        within the IconWidget's touch_boundary.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :type touch_point: Tuple[x,y]
        :return: Boolean
        """

        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        return super().contains((touch_x, touch_y, 0))

    def selected(self, touch_point):
        """Performs zoom animation when pressed.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :type touch_point: Tuple[x,y]
        :return: None
        """

        self.value = True

        if self._animation_time > 0:
            ###
            ## Create the zoom palette, bitmap and tilegrid
            ###

            # copy the image palette, add a transparent color at the end
            self._zoom_color_depth = len(self._palette) + 1

            self._zoom_palette = Palette(self._zoom_color_depth)
            for i in range(len(self._palette)):
                self._zoom_palette[i] = self._palette[i]
            self._zoom_palette[self._zoom_color_depth - 1] = 0x000000
            self._zoom_palette.make_transparent(self._zoom_color_depth - 1)

            # create the zoom bitmap larger than the original image to allow for zooming
            self._zoom_bitmap = Bitmap(
                round(self._image.width * self._end_scale),
                round(self._image.height * self._end_scale),
                len(self._zoom_palette),
            )
            self._zoom_bitmap.fill(self._zoom_color_depth - 1)  # transparent fill
            self._zoom_bitmap.blit(
                (self._zoom_bitmap.width - self._image.width) // 2,
                (self._zoom_bitmap.height - self._image.height) // 2,
                self._image,
            )  # blit the image into the center of the zoom_bitmap

            # place zoom_bitmap at same location as image
            self._zoom_tilegrid = TileGrid(
                self._zoom_bitmap, pixel_shader=self._zoom_palette
            )
            self._zoom_tilegrid.x = -(self._zoom_bitmap.width - self._image.width) // 2
            self._zoom_tilegrid.y = (
                -(self._zoom_bitmap.height - self._image.height) // 2
            )
            self.append(self._zoom_tilegrid)  # add to the self group.

            # Animation: zoom larger
            start_time = time.monotonic()
            while True:
                elapsed_time = time.monotonic() - start_time
                position = min(
                    1.0, easein(elapsed_time / self._animation_time)
                )  # fractional position
                bitmaptools.rotozoom(
                    dest_bitmap=self._zoom_bitmap,
                    ox=self._zoom_bitmap.width // 2,
                    oy=self._zoom_bitmap.height // 2,
                    source_bitmap=self._image,
                    px=self._image.width // 2,
                    py=self._image.height // 2,
                    scale=self._start_scale
                    + position * (self._end_scale - self._start_scale),
                    angle=position * self._angle / 2,
                )
                self.display.refresh()
                if elapsed_time > self._animation_time:
                    break

    def released(self, touch_point):
        """Performs un-zoom animation when released.

        :param touch_point: x,y location of the screen, converted to local coordinates.
        :type touch_point: Tuple[x,y]
        :return: None
        """

        if (self._animation_time > 0) and self.value:
            # Animation: shrink down to the original size
            start_time = time.monotonic()
            while True:
                elapsed_time = time.monotonic() - start_time
                position = max(0.0, easeout(1 - (elapsed_time / self._animation_time)))
                self._zoom_bitmap.fill(self._zoom_color_depth - 1)
                bitmaptools.rotozoom(
                    dest_bitmap=self._zoom_bitmap,
                    ox=self._zoom_bitmap.width // 2,
                    oy=self._zoom_bitmap.height // 2,
                    source_bitmap=self._image,
                    px=self._image.width // 2,
                    py=self._image.height // 2,
                    scale=self._start_scale
                    + position * (self._end_scale - self._start_scale),
                    angle=position * self._angle / 2,
                )
                self.display.refresh()
                if elapsed_time > self._animation_time:
                    break

            # clean up the zoom display elements
            self.pop(-1)  # remove self from the group
            del self._zoom_tilegrid
            del self._zoom_bitmap
            del self._zoom_palette
            gc.collect()

        self.value = False
