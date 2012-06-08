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

import sys
import math
from StringIO import StringIO

from gi.repository import Gtk, Champlain, Clutter, GLib

import EXIF

class PictureMarker(Champlain.CustomMarker):
    def __init__(self, img, thumb):
        Champlain.CustomMarker.__init__(self)

        lat_long = [0, 0]

        self._img = img
        self._thumbnail = thumb

        # draw our clickable marker
        marker = Clutter.Actor()
        purple = Clutter.Color.new(0xf0, 0x02, 0xf0, 0xbb)
        marker.set_background_color(purple)
        marker.set_size(15, 15)
        marker.set_position(0, 0)
        marker.set_anchor_point(0, 0)
        marker.set_reactive(True)
        self.add_actor(marker)
        marker.show()

        # our meta info
        self.group = Clutter.Group()
        self.group.set_position(20, 0)
        self.group.set_anchor_point(0, 0)
        self.add_actor(self.group)

        # just drawn a rectange or something
        rect = Clutter.Actor()
        c = Clutter.Color()
        c.from_string('#FFFFFFEE')
        rect.set_background_color(c)
        rect.set_size(200, 300)
        rect.set_position(0, 10)
        rect.set_anchor_point(0, 0)
        self.group.add_child(rect)

        self.name = Clutter.Text()
        self.name.set_text('Test Text')
        self.name.set_size(190, 25)
        self.name.set_position(5, 15)
        self.name.set_anchor_point(0, 0)
        self.group.add_child(self.name)

        thumb = None
        self.orientation = 0
        try:
            # get the exif info
            f = open(self._img, 'rb')
            tags = EXIF.process_file(f, details=False)
            lat = tags.get('GPS GPSLatitude', None)
            lon = tags.get('GPS GPSLongitude', None)
            lat_ref = tags.get('GPS GPSLatitudeRef', 'N')
            lon_ref = tags.get('GPS GPSLongitudeRef', 'W')

            # convert to lat/long
            # from:
            # http://www.nihilogic.dk/labs/gps_exif_google_maps/
            
            i = 1 if lat_ref is 'N' else -1
            flat = (lat.values[0].num / float(lat.values[0].den)) + \
                (lat.values[1].num / float(lat.values[1].den)) / 60.0 + \
                (lat.values[2].num /float(lat.values[2].den)) / 3600.0 * i

            j = 1 if lon_ref is 'W' else -1
            flon = (lon.values[0].num / float(lon.values[0].den)) + \
                (lon.values[1].num / float(lon.values[1].den)) / 60.0 + \
                (lon.values[2].num /float(lon.values[2].den)) / 3600.0 * j

            lat_long = [flat, flon]

            # orientation
            orientation_tag = tags.get('Image Orientation', None)
            
            if orientation_tag is not None:
                orientation_v = orientation_tag.values

                if orientation_v[0] == 8: # counter clock wise
                    self.orientation = -90
                    #self.picture.set_z_rotation_from_gravity(-90, Clutter.Gravity.CENTER)
                elif orientation_v[0] == 6: # clock wise
                    #self.picture.set_z_rotation_from_gravity(90, Clutter.Gravity.CENTER)
                    self.orientation = 90
                elif orientation_v[0] == 3: # 180
                    #self.picture.set_z_rotation_from_gravity(180, Clutter.Gravity.CENTER)
                    self.orientation = 180

            # thumbnail
            #t = tags.get('JPEGThumbnail', None)
            #if t:
            #    thumbnail = StringIO(t)

        except IOError, e:
            print >> sys.stderr, 'No GPS tags?', e

        # hide our meta
        self.group.hide_all()
        self._visible = False

        # our position
        self.set_location(lat_long[0], -lat_long[1])
        
        marker.connect('button-release-event', self.on_click)

        self.set_reactive(False)

    def on_click(self, actor, event):
        self._visible = not self._visible

        if self._visible:
            # create our texture
            try:
                self.picture = Clutter.Texture()
                if self._thumbnail:
                    self.picture.set_from_file(self._thumbnail)
                else:
                    self.picture.set_from_file(self._img)
                self.picture.set_keep_aspect_ratio(True)
                #self.picture.set_size(150, 150)
                self.picture.set_width(150)
                self.picture.set_position(25, 50)
                self.picture.set_anchor_point(0, 0)
                self.picture.set_z_rotation_from_gravity(self.orientation, Clutter.Gravity.CENTER)
                self.group.add_child(self.picture)
            except GLib.GError, e:
                print >> sys.stderr, e
                #!mwd - load a broken image instead?

            self.group.show_all()
        else:
            self.group.hide_all()
            self.group.remove_child(self.picture)
            self.picture = None

        return True

