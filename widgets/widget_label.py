# The MIT License (MIT)
#
# Copyright (c) 2021 Kevin Matocha (kmatch98)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# CircuitPython GUI Widget Class for visual elements
#
# Properties:
#   - name
# 	- font
#	- anchor_point
#	- anchor_point_on_widget

import displayio
from adafruit_display_text import bitmap_label

class WidgetLabel(bitmap_label.Label):
    """A WidgetLabel class to connect a label to a widget.
    The ``anchor_point`` and ``anchor_point_on_widget`` along with
    the widget's ``bounding_box`` are used to position the label."""

    def __init__(
    	self,
    	font,
    	Widget,
    	anchor_point_on_widget=None,
    	**kwargs,
    	):

<<<<<<< HEAD
=======
    	for arg in kwargs:
    		print(arg)

>>>>>>> 4dfdce6 (Initial commit with Widget, Control and WidgetLabel class definitions, includes horizontal switch widget definition and PyPortal example)
		super().__init__(font, text=Widget.name, **kwargs)

		self.anchor_point_on_widget = anchor_point_on_widget
		self.update_label_position(Widget.bounding_box)
		Widget.append(self)


    # Widget label position is adjusted so that the ``anchor_point`` on the label
    # is set to the ``anchor_point_on_widget`` location.  This function requires
    # the widget's ``bounding_box`` as a parameter.
    def update_label_position(self, bounding_box):

		if ( (bounding_box is None) or
			(self.anchor_point is None) or
			(self.anchor_point_on_widget) is None ):
			pass

		else:
			x0 = bounding_box[0]
			y0 = bounding_box[1]
			width = bounding_box[2]
			height = bounding_box[3]

			anchored_position_x = x0 + int(width  * self.anchor_point_on_widget[0])
			anchored_position_y = y0 + int(height * self.anchor_point_on_widget[1])

			self.anchored_position=(anchored_position_x, anchored_position_y)



