# SPDX-FileCopyrightText: 2022 Tim Cocks
#
# SPDX-License-Identifier: MIT

"""
`page_layout`
================================================================================

A layout that organizes pages which can be viewed one at a time.


* Author(s): Tim Cocks

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
try:
    # Used only for typing
    # pylint: disable=unused-import
    from typing import Tuple

except ImportError:
    pass

import displayio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout.git"


class PageLayout(displayio.Group):
    """
    A layout that organizes children into a grid table structure.

    :param int x: x location the layout should be placed. Pixel coordinates.
    :param int y: y location the layout should be placed. Pixel coordinates.
    """

    def __init__(
        self,
        x,
        y,
    ):
        super().__init__(x=x, y=y)
        self.x = x
        self.y = y

        self.page_content_list = []
        self._cur_showing_index = 0

    def add_content(self, page_content, page_name=None):
        """Add a child to the page layout.

        :param page_content: the content for the page typically a Group
        :param page_name: the name of this page

        :return: None"""

        _page_group = displayio.Group()
        _page_group.append(page_content)

        sub_view_obj = {
            "content": _page_group,
            "page_name": page_name,
        }

        if len(self.page_content_list) > 0:
            _page_group.hidden = True

        self.page_content_list.append(sub_view_obj)
        self.append(_page_group)

    def _check_args(self, page_name, page_index):
        """
        Ensure supplied arguments are valid

        :param string page_name: name of a page
        :param int page_index: index of a page
        :return: None
        """
        if page_name is None and page_index is None:
            raise AttributeError("Must pass either page_name or page_index")

        if page_index is not None and page_name is not None:
            raise AttributeError(
                "Must pass either page_name or page_index only one or the other"
            )

        if page_index is not None:
            if page_index >= len(self.page_content_list):
                raise KeyError(
                    "KeyError at index {} in list length {}".format(
                        page_index, len(self.page_content_list)
                    ),
                )

        if page_name is not None:
            _found = False
            for page in self.page_content_list:
                if not _found:
                    if page_name == page["page_name"]:
                        _found = True

            if not _found:
                raise KeyError("Page with name {} not found".format(page_name))

    def get_page(self, page_name=None, page_index=None):
        """
        Return a page content based on the name or index. Raises
        KeyError if the page was not found in the PageLayout.

        :param string page_name: the name of the page to lookup
        :param int page_index: the index of the page to lookup
        :return: the displayio content object at those coordinates
        """

        self._check_args(page_name, page_index)

        if page_index is not None:
            return self.page_content_list[page_index]

        if page_name is not None:
            for cell in self.page_content_list:
                if cell["page_name"] == page_name:
                    return cell

        raise KeyError(
            "PageLayout does not contain page: {}".format(
                page_index if page_index else page_name
            )
        )

    def show_page(self, page_name=None, page_index=None):
        """
        Show the specified page, and hide all other pages.

        :param string page_name: The name of a page to show
        :param int page_index: The index of a page to show
        :return: None
        """

        self._check_args(page_name, page_index)

        for cur_index, page in enumerate(self.page_content_list):
            if page_name is not None:
                if page["page_name"] == page_name:
                    self._cur_showing_index = cur_index
                    page["content"].hidden = False
                else:
                    page["content"].hidden = True

            if page_index is not None:
                if cur_index == page_index:
                    self._cur_showing_index = cur_index
                    page["content"].hidden = False
                else:
                    page["content"].hidden = True

    @property
    def showing_page_index(self):
        """
        Index of the currently showing page
        :return int: showing_page_index
        """
        return self._cur_showing_index

    @showing_page_index.setter
    def showing_page_index(self, new_index):
        self.show_page(page_index=new_index)

    @property
    def showing_page_name(self):
        """
        Name of the currently showing page
        :return string: showing_page_name
        """
        return self.page_content_list[self._cur_showing_index]["page_name"]

    @showing_page_name.setter
    def showing_page_name(self, new_name):
        self.show_page(page_name=new_name)

    @property
    def showing_page_content(self):
        """
        The content object for the currently showing page
        :return Displayable: showing_page_content
        """
        return self.page_content_list[self._cur_showing_index]["content"][0]

    def next_page(self, loop=True):
        """
        Hide the current page and show the next one in the list by index
        :param bool loop: whether to loop from the last page back to the first
        :return: None
        """

        if self._cur_showing_index + 1 < len(self.page_content_list):
            self.show_page(page_index=self._cur_showing_index + 1)
        else:
            if not loop:
                print("No more pages")
            else:
                self.show_page(page_index=0)

    def previous_page(self, loop=True):
        """
        Hide the current page and show the previous one in the list by index
        :param bool loop: whether to loop from the first page to the last one
        :return: None
        """
        if self._cur_showing_index - 1 >= 0:
            self.show_page(page_index=self._cur_showing_index - 1)
        else:
            if not loop:
                print("No more pages")
            else:
                self.show_page(page_index=len(self.page_content_list) - 1)
