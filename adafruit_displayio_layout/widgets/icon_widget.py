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


import terminalio
from displayio import TileGrid, OnDiskBitmap
import adafruit_imageload
from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.widgets.control import Control
from adafruit_displayio_layout.widgets.widget import Widget

try:
    from typing import Any, Optional, Tuple
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class IconWidget(Widget, Control):

    """
    A touch enabled widget that holds an icon image loaded with
    adafruit_imageload and a text label centered beneath it.

    :param string label_text: the text that will be shown beneath the icon image.
    :param string icon: the filepath of the bmp image to be used as the icon.
    :param boolean on_disk: if True use OnDiskBitmap instead of imageload.
     This can be helpful to save memory. Defaults to False
    :param Optional[int] transparent_index: if not None this color index will get set to
     transparent on the palette of the icon.
    :param Optional[int] label_background: if not None this color will be used as a background
     for the icon label.
    :param int x: x location the icon widget should be placed. Pixel coordinates.
    :param int y: y location the icon widget should be placed. Pixel coordinates.
    :param anchor_point: (X,Y) values from 0.0 to 1.0 to define the anchor point relative to the
     widget bounding box
    :type anchor_point: Tuple[float,float]
    :param int anchored_position: (x,y) pixel value for the location of the anchor_point
    :type anchored_position: Tuple[int, int]
    """

    # pylint: disable=too-many-arguments

    def __init__(
        self,
        label_text: str,
        icon: str,
        on_disk: bool = False,
        transparent_index: Optional[int] = None,
        label_background: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self._icon = icon

        if on_disk:
            image = OnDiskBitmap(self._icon)
            if transparent_index is not None:
                image.pixel_shader.make_transparent(transparent_index)
            tile_grid = TileGrid(image, pixel_shader=image.pixel_shader)
        else:
            image, palette = adafruit_imageload.load(icon)
            if transparent_index is not None:
                palette.make_transparent(transparent_index)
            tile_grid = TileGrid(image, pixel_shader=palette)
        self.append(tile_grid)
        _label = bitmap_label.Label(
            terminalio.FONT,
            scale=1,
            text=label_text,
            anchor_point=(0.5, 0),
            anchored_position=(image.width // 2, image.height),
        )

        if label_background is not None:
            _label.background_color = label_background

        self.append(_label)
        self.touch_boundary: Tuple[int, int, int, int] = (
            0,
            0,
            image.width,
            image.height + _label.bounding_box[3],
        )

    def contains(
        self, touch_point: Tuple[int, int, Optional[int]]
    ) -> bool:  # overrides, then calls Control.contains(x,y)
        """Checks if the IconWidget was touched.  Returns True if the touch_point is
        within the IconWidget's touch_boundary.

        :param touch_point: x, y, p location of the screen, converted to local coordinates, plus
            an optional pressure value for screens that support it.
        :type touch_point: Tuple[int, int, Optional[int]]
        :return: Boolean
        """

        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        return super().contains((touch_x, touch_y, 0))
