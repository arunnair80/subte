#
# Copyright (C) 2012 - Marcus Dillavou
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

from gi.repository import Gtk, Champlain, GtkChamplain, Clutter

class GTMap(GtkChamplain.Embed):
    def __init__(self):
        GtkChamplain.Embed.__init__(self)

        # give ourselves an initial size
        self.set_size_request(640, 480)

        self.view = self.get_view()

        # our bus station layer
        self.stop_layer = Champlain.MarkerLayer()
        self.view.add_layer(self.stop_layer)
        self.stop_layer.show()
        self.stop_layer.show_all_markers()

        # !mwd - temp
        self.view.go_to(33.511878, -86.808826)
        self.view.set_zoom_level(14)
        self.view.set_kinetic_mode(True)
        
        self.view.set_reactive(True)
        self.view.connect('button-release-event', self.on_click)

    def on_click(self, view, event):
        print 'on-click', view, event
        x, y = event.get_coords()
        print view.x_to_longitude(x), view.y_to_latitude(y)

        # add a random place maker
        import random

        purple = Clutter.Color.new(0xf0, 0x02, 0xf0, 0xbb)

        marker = Champlain.Label.new_with_text('Stop %d' % random.randint(0, 1000),
                                               'Serif 14', None, purple)
        marker.set_use_markup(True)
        marker.set_color(purple)
        marker.set_location(view.y_to_latitude(y), view.x_to_longitude(x))
        marker.set_reactive(True)
        marker.connect('button-release-event', self.on_marker_click)
        self.stop_layer.add_marker(marker)

        #self.stop_layer.animate_in_all_markers()
        marker.animate_in()
        print 'marker=', marker

        return True

    def on_marker_click(self, actor, event):
        print 'on_marker_click', actor, event

        return False
    