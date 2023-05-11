# SPDX-FileCopyrightText: 2022 Tim Cocks
#
# SPDX-License-Identifier: MIT

"""
`tab_layout`
================================================================================

A layout that organizes pages into tabs.


* Author(s): Tim Cocks

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
try:
    from typing import Optional, Union, Tuple
    from fontio import BuiltinFont
    from adafruit_bitmap_font.bdf import BDF
    from adafruit_bitmap_font.pcf import PCF
except ImportError:
    pass

import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text.bitmap_label import Label
from adafruit_imageload.tilegrid_inflator import inflate_tilegrid
from adafruit_displayio_layout.layouts.page_layout import PageLayout

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class TabLayout(displayio.Group):
    """
    A layout that organizes children into a grid table structure.

    .. warning::
        Requires CircuitPython version 7.3.0-beta.2 or newer

    :param int x: x location the layout should be placed. Pixel coordinates.
    :param int y: y location the layout should be placed. Pixel coordinates.
    :param displayio.Display display: The Display object to show the tab layout on.
    :param int tab_text_scale: Size of the text shown in the tabs.
      Whole numbers 1 and greater are valid
    :param Optional[Union[BuiltinFont, BDF, PCF]] custom_font: A pre-loaded font object to use
      for the tab labels
    :param str inactive_tab_spritesheet: Filepath of the spritesheet to show for inactive tabs.
    :param str showing_tab_spritesheet: Filepath of the spritesheet to show for the active tab.
    :param Optional[int, tuple[int, int, int]] showing_tab_text_color: Hex or tuple color to use
      for the active tab label
    :param Optional[int, tuple[int, int, int]] inactive_tab_text_color: Hex or tuple color to
      use for inactive tab labels
    :param Optional[Union[int, tuple[int, int]]] inactive_tab_transparent_indexes: single index
      or tuple of multiple indexes to be made transparent in the inactive tab sprite palette.
    :param Optional[Union[int, tuple[int, int]]] showing_tab_transparent_indexes: single index
      or tuple of multiple indexes to be made transparent in the active tab sprite palette.
    :param int tab_count: How many tabs to draw in the layout. Positive whole numbers are valid.
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments, invalid-name, too-many-branches

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        display: Optional[displayio.Display] = None,
        tab_text_scale: int = 1,
        custom_font: Optional[Union[BuiltinFont, BDF, PCF]] = terminalio.FONT,
        inactive_tab_spritesheet: Optional[str] = None,
        showing_tab_spritesheet: Optional[str] = None,
        showing_tab_text_color: Optional[Union[int, Tuple[int, int, int]]] = 0x999999,
        inactive_tab_text_color: Optional[Union[int, Tuple[int, int, int]]] = 0xFFFFF,
        inactive_tab_transparent_indexes: Optional[Union[int, Tuple[int, int]]] = None,
        showing_tab_transparent_indexes: Optional[Union[int, Tuple[int, int]]] = None,
        tab_count: int = None,
    ):
        if display is None:
            # pylint: disable=import-outside-toplevel
            import board

            if hasattr(board, "DISPLAY"):
                display = board.DISPLAY
        if inactive_tab_spritesheet is None:
            raise AttributeError("Must pass inactive_tab_spritesheet")
        if showing_tab_spritesheet is None:
            raise AttributeError("Must pass showing_tab_spritesheet")
        if tab_count is None:
            raise AttributeError("Must pass tab_count")

        super().__init__(x=x, y=y)
        self.tab_count = tab_count
        self._active_bmp, self._active_palette = adafruit_imageload.load(
            showing_tab_spritesheet
        )
        self._inactive_bmp, self._inactive_palette = adafruit_imageload.load(
            inactive_tab_spritesheet
        )

        if isinstance(showing_tab_transparent_indexes, int):
            self._active_palette.make_transparent(showing_tab_transparent_indexes)
        elif isinstance(showing_tab_transparent_indexes, tuple):
            for index in showing_tab_transparent_indexes:
                self._active_palette.make_transparent(index)
        else:
            raise AttributeError("active_tab_transparent_indexes must be int or tuple")

        if isinstance(inactive_tab_transparent_indexes, int):
            self._inactive_palette.make_transparent(inactive_tab_transparent_indexes)
        elif isinstance(inactive_tab_transparent_indexes, tuple):
            for index in inactive_tab_transparent_indexes:
                self._inactive_palette.make_transparent(index)
        else:
            raise AttributeError(
                "inactive_tab_transparent_indexes must be int or tuple"
            )

        self.tab_height = self._active_bmp.height
        self.display = display
        self.active_tab_text_color = showing_tab_text_color
        self.inactive_tab_text_color = inactive_tab_text_color
        self.custom_font = custom_font
        self.tab_text_scale = tab_text_scale
        self.tab_group = displayio.Group()
        self.tab_dict = {}
        self.page_layout = PageLayout(x=x, y=y + self.tab_height)

        self.append(self.tab_group)
        self.append(self.page_layout)

    def _draw_tabs(self):
        for i, page_dict in enumerate(self.page_layout.page_content_list):
            if i not in self.tab_dict:
                print(f"creating tab {i}")
                _new_tab_group = displayio.Group()
                _tab_tilegrid = inflate_tilegrid(
                    bmp_obj=self._inactive_bmp,
                    bmp_palette=self._inactive_palette,
                    target_size=(
                        (self.display.width // self.tab_count)
                        // (self._active_bmp.width // 3),
                        3,
                    ),
                )

                _tab_tilegrid.x = (self.display.width // self.tab_count) * i
                _new_tab_group.append(_tab_tilegrid)

                _tab_label = Label(
                    self.custom_font,
                    text=page_dict["page_name"],
                    color=self.inactive_tab_text_color,
                    scale=self.tab_text_scale,
                )

                _tab_label.anchor_point = (0.5, 0.5)
                _tab_label.anchored_position = (
                    _tab_tilegrid.x
                    + ((_tab_tilegrid.width * _tab_tilegrid.tile_width) // 2),
                    (_tab_tilegrid.height * _tab_tilegrid.tile_height) // 2,
                )
                _new_tab_group.append(_tab_label)

                if i == self.page_layout.showing_page_index:
                    try:
                        _tab_tilegrid.bitmap = self._active_bmp
                    except AttributeError as e:
                        print(e)
                        raise (
                            AttributeError(
                                "TabLayout requires CircuitPython version 7.3.0-beta.2 or newer."
                            )
                        ) from e
                    _tab_tilegrid.pixel_shader = self._active_palette
                    _tab_label.color = self.active_tab_text_color
                self.tab_dict[i] = _new_tab_group
                self.tab_group.append(_new_tab_group)

    def _update_active_tab(self):
        for i in range(len(self.page_layout)):
            if i == self.page_layout.showing_page_index:
                self.tab_group[i][0].bitmap = self._active_bmp
                self.tab_group[i][0].pixel_shader = self._active_palette
                self.tab_group[i][1].color = self.active_tab_text_color
            else:
                self.tab_group[i][0].bitmap = self._inactive_bmp
                self.tab_group[i][0].pixel_shader = self._inactive_palette
                self.tab_group[i][1].color = self.inactive_tab_text_color

    def add_content(self, tab_content, tab_name):
        """Add a child to the tab layout.

        :param tab_content: the content for the tab typically a Group
        :param tab_name: the name of this tab, will be shown inside the tab

        :return: None"""
        self.page_layout.add_content(tab_content, tab_name)
        self._draw_tabs()

    def show_page(self, page_name=None, page_index=None):
        """
        Show the specified page, and hide all other pages.

        :param string page_name: The name of a page to show
        :param int page_index: The index of a page to show
        :return: None
        """

        self.page_layout.show_page(page_name=page_name, page_index=page_index)
        self._update_active_tab()

    @property
    def showing_page_index(self):
        """
        Index of the currently showing page
        :return int: showing_page_index
        """
        return self.page_layout.showing_page_index

    @showing_page_index.setter
    def showing_page_index(self, new_index):
        if self.showing_page_index != new_index:
            self.show_page(page_index=new_index)

    @property
    def showing_page_name(self):
        """
        Name of the currently showing page
        :return string: showing_page_name
        """
        return self.page_layout.showing_page_name

    @showing_page_name.setter
    def showing_page_name(self, new_name):
        self.show_page(page_name=new_name)

    @property
    def showing_page_content(self):
        """
        The content object for the currently showing page
        :return Displayable: showing_page_content
        """
        return self.page_layout.showing_page_content

    def next_page(self, loop=True):
        """
        Hide the current page and show the next one in the list by index
        :param bool loop: whether to loop from the last page back to the first
        :return: None
        """

        self.page_layout.next_page(loop=loop)
        self._update_active_tab()

    def previous_page(self, loop=True):
        """
        Hide the current page and show the previous one in the list by index
        :param bool loop: whether to loop from the first page to the last one
        :return: None
        """
        self.page_layout.previous_page(loop=loop)
        self._update_active_tab()

    def handle_touch_events(self, touch_event):
        """
        Check if the touch event is on the tabs and if so change to the touched tab.

        :param tuple touch_event: tuple containing x and y coordinates of the
          touch event in indexes 0 and 1.
        :return: None
        """

        if touch_event:
            if 0 <= touch_event[1] <= self.tab_height:
                touched_tab_index = touch_event[0] // (
                    self.display.width // self.tab_count
                )
                print(f"{touch_event[0]} - {touched_tab_index}")
                self.showing_page_index = touched_tab_index
