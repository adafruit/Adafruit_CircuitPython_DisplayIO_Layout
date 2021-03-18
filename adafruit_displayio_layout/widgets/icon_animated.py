# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
"""

`icon_animated`
================================================================================
A touch enabled widget that includes an animated icon image with a small text label
centered below it.

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import gc
import time
import bitmaptools
from displayio import TileGrid, Bitmap, Palette
import adafruit_imageload
from adafruit_displayio_layout.widgets.icon_widget import IconWidget
from adafruit_displayio_layout.widgets.easing import quadratic_easeout as easein
from adafruit_displayio_layout.widgets.easing import quadratic_easein as easeout


class IconAnimated(IconWidget):

    """
    An animated touch enabled widget that holds an icon image loaded with
    OnDiskBitmap and a text label centered beneath it. Includes optional
    animation to increase the icon size when pressed.

    .. Warning::  The `init_class` class function should be called before instancing any
        IconAnimated widgets.

    :param str label_text: the text that will be shown beneath the icon image.
    :param str icon: the filepath of the bmp image to be used as the icon.
    :param bool on_disk: if True use OnDiskBitmap instead of imageload.
     This can be helpful to save memory. Defaults to False

    :param float max_scale: the maximum zoom during animation, set 1.0 for no animation
     a value of 1.4 is a good starting point (default: 1.0, no animation),
     ``max_scale`` must be between 1.0 and 1.5.
    :param float max_angle: the maximum degrees of rotation during animation, positive values
     are clockwise, set 0 for no rotation, in degrees (default: 0 degrees)
    :param float animation_time: the time for the animation in seconds, set to 0.0 for
     no animation, a value of 0.15 is a good starting point (default: 0.0 seconds)

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

    # pylint: disable=bad-super-call, too-many-instance-attributes, too-many-locals
    # pylint: disable=too-many-arguments, unused-argument

    display = None
    # The other Class variables are created in Class method `init_class`:
    #               max_scale, bitmap_buffer, palette_buffer

    @classmethod
    def init_class(
        cls, display=None, max_scale=1.5, max_size=(80, 80), max_color_depth=512
    ):
        """
        Initializes the IconAnimated Class variables, including preallocating memory
        buffers for the icon zoom bitmap and icon palette.

        .. Note::  The `init_class` class function should be called before instancing any
                IconAnimated widgets. Usage example:
                ``IconAnimated(display=board.DISPLAY, max_scale=1.5,
                max_size=(80,80), max_color_depth=256)``

        :param displayio.Display display: The display where the icons will be displayed.
        :param float max_scale: The maximum zoom of the any of the icons, should be > 1.0,
         (default: 1.5)
        :param max_size: The maximum (x,y) pixel dimensions of any `IconAnimated` bitmap size
         that will be created (default: (80,80))
        :type max_size: Tuple[int,int]
        :param int max_color_depth: The maximum color depth of any `IconAnimated`
         bitmap that will be created (default: 512)
        """
        if display is None:
            raise ValueError("Must provide display parameter for IconAnimated.")
        cls.display = display
        cls.max_scale = max(1.0, max_scale)
        cls.bitmap_buffer = Bitmap(
            round(max_scale * max_size[0]),
            round(max_scale * max_size[1]),
            max_color_depth + 1,
        )
        cls.palette_buffer = Palette(max_color_depth + 1)

    def __init__(
        self,
        label_text,
        icon,
        on_disk=False,
        max_scale=1.4,
        max_angle=8,
        animation_time=0.15,
        **kwargs,
    ):

        if self.__class__.display is None:
            raise ValueError(
                "Must initialize class using\n"
                "`IconAnimated.init_class(display, max_scale, max_size, max_color_depth)`\n"
                "prior to instancing IconAnimated widgets."
            )

        super().__init__(label_text, icon, on_disk, **kwargs)  # initialize superclasses

        # constrain instance's maximum_scaling between 1.0 and the Class's max_scale
        self._max_scale = min(max(1.0, max_scale), self.__class__.max_scale)
        if max_scale == 1.0:  # no animation
            self._animation_time = 0
        else:
            self._animation_time = animation_time  # in seconds
        self._angle = (max_angle / 360) * 2 * 3.14  # 5 degrees, convert to radians
        self._zoomed = False  # state variable for zoom status

    def zoom_animation(self, touch_point):
        """Performs zoom animation when icon is pressed.

        :param touch_point: x,y location of the screen.
        :type touch_point: Tuple[x,y]
        :return: None
        """

        if self._animation_time > 0:
            ###
            ## Update the zoom palette and bitmap buffers and append the tilegrid
            ###

            _image, _palette = adafruit_imageload.load(self._icon)
            animation_bitmap = self.__class__.bitmap_buffer
            animation_palette = self.__class__.palette_buffer

            # copy the image palette, add a transparent color at the end
            for i, color in enumerate(_palette):
                animation_palette[i] = color
            animation_palette[len(animation_palette) - 1] = 0x000000
            animation_palette.make_transparent(len(animation_palette) - 1)

            # create the zoom bitmap larger than the original image to allow for zooming
            animation_bitmap.fill(len(animation_palette) - 1)  # transparent fill
            animation_bitmap.blit(
                (animation_bitmap.width - _image.width) // 2,
                (animation_bitmap.height - _image.height) // 2,
                _image,
            )  # blit the image into the center of the zoom_bitmap

            # place zoom_bitmap at same location as image
            animation_tilegrid = TileGrid(
                animation_bitmap, pixel_shader=animation_palette
            )
            animation_tilegrid.x = -(animation_bitmap.width - _image.width) // 2
            animation_tilegrid.y = -(animation_bitmap.height - _image.height) // 2
            self.append(animation_tilegrid)  # add to the self group.

            # Animation: zoom larger
            start_time = time.monotonic()
            while True:
                elapsed_time = time.monotonic() - start_time
                position = min(
                    1.0, easein(elapsed_time / self._animation_time)
                )  # fractional position
                bitmaptools.rotozoom(
                    dest_bitmap=animation_bitmap,
                    ox=animation_bitmap.width // 2,
                    oy=animation_bitmap.height // 2,
                    source_bitmap=_image,
                    px=_image.width // 2,
                    py=_image.height // 2,
                    scale=1.0  # start scaling at 1.0
                    + position * (self._max_scale - 1.0),
                    angle=position * self._angle / 2,
                )
                self.__class__.display.refresh()
                if elapsed_time > self._animation_time:
                    break
            del _image
            del _palette
            gc.collect()

            self._zoomed = True

    def zoom_out_animation(self, touch_point):
        """Performs un-zoom animation when icon is released.

        :param touch_point: x,y location of the screen.
        :type touch_point: Tuple[x,y]
        :return: None
        """

        _image, _palette = adafruit_imageload.load(self._icon)
        animation_bitmap = self.__class__.bitmap_buffer
        animation_palette = self.__class__.palette_buffer

        if (self._animation_time > 0) and self._zoomed:
            # Animation: shrink down to the original size
            start_time = time.monotonic()
            while True:
                elapsed_time = time.monotonic() - start_time
                position = max(0.0, easeout(1 - (elapsed_time / self._animation_time)))
                animation_bitmap.fill(len(animation_palette) - 1)
                bitmaptools.rotozoom(
                    dest_bitmap=animation_bitmap,
                    ox=animation_bitmap.width // 2,
                    oy=animation_bitmap.height // 2,
                    source_bitmap=_image,
                    px=_image.width // 2,
                    py=_image.height // 2,
                    scale=1.0 + position * (self._max_scale - 1.0),
                    angle=position * self._angle / 2,
                )
                self.__class__.display.refresh()
                if elapsed_time > self._animation_time:
                    break

            # clean up the zoom display elements
            self.pop(-1)  # remove self from the group
            del _image
            del _palette
            gc.collect()

        self._zoomed = False
