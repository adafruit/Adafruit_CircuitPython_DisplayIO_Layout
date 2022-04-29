
try:
    from typing import Optional, Union
    from fontio import BuiltinFont
    from adafruit_bitmap_font.bdf import BDF
    from adafruit_bitmap_font.pcf import PCF
except ImportError:
    pass

import board
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text.bitmap_label import Label
from adafruit_imageload.tilegrid_inflator import inflate_tilegrid
from adafruit_displayio_layout.layouts.page_layout import PageLayout

class TabLayout(displayio.Group):
    def __init__(self,
                 x: int = 0, y: int = 0,
                 display: displayio.Display = board.DISPLAY,
                 tab_text_scale: int = 1,
                 custom_font: Optional[Union[BuiltinFont, BDF, PCF]] = terminalio.FONT,
                 inactive_tab_spritesheet: Optional[str] = None,
                 active_tab_spritesheet: Optional[str] = None,
                 active_tab_text_color: Optional[int, tuple[int, int, int]] = 0x999999,
                 inactive_tab_text_color: Optional[int, tuple[int, int, int]] = 0xfffff,
                 inactive_tab_transparent_indexes: Optional[Union[int, tuple[int, int]]] = None,
                 active_tab_transparent_indexes: Optional[Union[int, tuple[int, int]]] = None,
                 tab_count: int = None,
                 ):

        if inactive_tab_spritesheet is None:
            raise AttributeError("Must pass active_tab_spritesheet")
        if active_tab_spritesheet is None:
            raise AttributeError("Must pass inactive_tab_spritesheet")
        if tab_count is None:
            raise AttributeError("Must pass tab_count")

        super().__init__(x=x, y=y)
        self.tab_count = tab_count
        self._active_bmp, self._active_palette = adafruit_imageload.load(active_tab_spritesheet)
        self._inactive_bmp, self._inactive_palette = adafruit_imageload.load(inactive_tab_spritesheet)

        if isinstance(active_tab_transparent_indexes, int):
            self._active_palette.make_transparent(active_tab_transparent_indexes)
        elif isinstance(active_tab_transparent_indexes, tuple):
            for index in active_tab_transparent_indexes:
                self._active_palette.make_transparent(index)
        else:
            raise AttributeError("active_tab_transparent_indexes must be int or tuple")

        if isinstance(inactive_tab_transparent_indexes, int):
            self._inactive_palette.make_transparent(inactive_tab_transparent_indexes)
        elif isinstance(inactive_tab_transparent_indexes, tuple):
            for index in inactive_tab_transparent_indexes:
                self._inactive_palette.make_transparent(index)
        else:
            raise AttributeError("inactive_tab_transparent_indexes must be int or tuple")

        self.tab_height = self._active_bmp.height
        self.display = display
        self.active_tab_text_color = active_tab_text_color
        self.inactive_tab_text_color = inactive_tab_text_color
        self.custom_font = custom_font
        self.tab_text_scale = tab_text_scale
        self.tab_group = displayio.Group()
        self.tab_dict = {}
        self.page_layout = PageLayout(x=x, y=y + self.tab_height)

        self.append(self.tab_group)
        self.append(self.page_layout)

    def _draw_tabs(self):
        for i, page_dict in enumerate(self.page_layout._page_content_list):
            if i not in self.tab_dict:
                print(f"creating tab {i}")
                _new_tab_group = displayio.Group()
                _tab_tilegrid = inflate_tilegrid(bmp_obj=self._inactive_bmp, bmp_palette=self._inactive_palette,
                                                 target_size=((self.display.width // self.tab_count) // (
                                                         self._active_bmp.width // 3), 3))

                _tab_tilegrid.x = (self.display.width // self.tab_count) * i
                _new_tab_group.append(_tab_tilegrid)

                _tab_label = Label(self.custom_font, text=page_dict["page_name"],
                                   color=self.inactive_tab_text_color, scale=self.tab_text_scale)

                _tab_label.anchor_point = (0.5, 0.5)
                _tab_label.anchored_position = (
                    _tab_tilegrid.x +
                    ((_tab_tilegrid.width * _tab_tilegrid.tile_width) // 2),
                    (_tab_tilegrid.height * _tab_tilegrid.tile_height) // 2
                )
                _new_tab_group.append(_tab_label)

                if i == self.page_layout.showing_page_index:
                    _tab_tilegrid.bitmap = self._active_bmp
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
