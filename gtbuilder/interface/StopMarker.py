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
import weakref

from gi.repository import Gtk, Champlain, Clutter, GLib

import gtbuilder

class StopMarker(Champlain.CustomMarker):
    def __init__(self, gtmap, stop):
        Champlain.CustomMarker.__init__(self)

        self._gtmap = None
        self.gtmap = gtmap

        self._stop = None
        self.stop = stop

        self.full_picture_box = None

        # draw our clickable marker
        self.marker = Clutter.Actor()
        purple = Clutter.Color.new(0xf0, 0x02, 0xf0, 0xbb)
        yellow = Clutter.Color.new(0xfd, 0xfd, 0x02, 0xbb)
        self.marker.set_background_color(purple)
        #self.marker.set_selection_color(yellow)
        self.marker.set_size(15, 15)
        self.marker.set_position(0, 0)
        self.marker.set_anchor_point(0, 0)
        self.marker.set_reactive(True)
        self.add_actor(self.marker)
        self.marker.show()

        self._visible = False

        self.set_location(self.stop.latitude, self.stop.longitude)

        # trying to capture it, then make us emit a signal doesn't
        #  seem to be working
        #self.marker.connect('button-release-event', self.on_click)

        self.set_reactive(False)

    @property
    def gtmap(self):
        if self._gtmap:
            return self._gtmap()
        return None
    @gtmap.setter
    def gtmap(self, m):
        if m:
            self._gtmap = weakref.ref(m)
        else:
            self._gtmap = None

    @property
    def stop(self):
        if self._stop:
            return self._stop()
        return None
    @stop.setter
    def stop(self, m):
        if m:
            self._stop = weakref.ref(m)
        else:
            self._stop = None
            
    def selected(self, status):
        #self.marker.selected = status
        return True

    def clicked(self, status):
        if status == self._visible: # nothing to do here
            return True

        if status:
            self.show()
        else:
            self.hide()

        return True

    def on_click(self, actor, event, user_data = None):
        #!mwd - this doesn't work :(
        print 'on_click and emitting', actor, event
        self.emit('button-release-event', event)
        return True

    def on_expand_picture(self, actor, event, picture):
        self.full_picture_box = Clutter.Texture()
        self.full_picture_box.set_from_file(picture.image)
        self.full_picture_box.set_keep_aspect_ratio(True)

        size = self.gtmap.get_allocated_width(), self.gtmap.get_allocated_height()
        r1 = size[0] / float(size[1])
        size2 = self.full_picture_box.get_base_size()

        if picture.orientation == 0 or picture.orientation == 180:
            r2 = size2[0] / float(size2[1])
        else:
            r2 = size2[1] / float(size2[0])

        self.full_picture_box.set_position(0, 0)
        self.full_picture_box.set_z_rotation_from_gravity(picture.orientation, Clutter.Gravity.CENTER)

        if r1 > r2: # use width
            w = size[1] * r2
            h = size[1] 
        else: # use height
            w = size[0]
            h = size[0] / r2

        if picture.orientation != 0 and picture.orientation != 180:
            w, h = h, w # reverse
        self.full_picture_box.set_size(w, h)


        self.full_picture_box.set_reactive(True)
        self.full_picture_box.connect('button-release-event', self.on_close_picture)
        self.full_picture_box.show_all()

        self.gtmap.show_image(self.full_picture_box)

        return False

    def on_close_picture(self, actor, event):
        if self.full_picture_box:
            self.gtmap.remove_image(self.full_picture_box)
            self.full_picture_box.hide_all()
        self.full_picture_box = None

        return False

    def show(self):
        print 'show'
        self.gtmap.unshow_stop_info()

        # our meta info
        group = Clutter.Group()
        group.set_position(20, 0)
        group.set_anchor_point(0, 0)
        #self.add_actor(group)

        # just drawn a rectange or something
        rect = Clutter.Actor()
        c = Clutter.Color.new(0xf0, 0xf0, 0xf0, 0xfe)
        rect.set_background_color(c)
        rect.set_size(200, 270)
        rect.set_position(0, 10)
        rect.set_anchor_point(0, 0)
        group.add_child(rect)

        name = Clutter.Text()
        if self.stop.name:
            name.set_text(self.stop.name)
        else:
            name.set_text('%s' % self.stop.stop_id)
        name.set_size(190, 25)
        name.set_position(20, 15)
        name.set_anchor_point(0, 0)
        group.add_child(name)

        info = Clutter.Text()
        info.set_use_markup(True)
        info.set_text('')
        info.set_size(190, 150)
        info.set_position(5, 210)
        info.set_anchor_point(0, 0)
        group.add_child(info)

        info.set_markup('<markup><big><b>GPS Info:</b></big>\n<b>Latitude:</b> %s\n<b>Longitude:</b> %s</markup>' % (self.stop.latitude, self.stop.longitude))

        # see if we have a picture (or more)
        if len(self.stop.pictures) > 0:
            try:
                picture_box = Clutter.Texture()

                # just use the first picture for now
                picture = self.stop.pictures[0]

                if picture.thumbnail:
                    picture_box.set_from_file(picture.thumbnail)
                else:
                    picture_box.set_from_file(picture.image)
                picture_box.set_keep_aspect_ratio(True)
                picture_box.set_width(150)
                picture_box.set_position(25, 60)
                picture_box.set_anchor_point(0, 0)
                picture_box.set_z_rotation_from_gravity(picture.orientation, Clutter.Gravity.CENTER)
                picture_box.connect('button-release-event', self.on_expand_picture, picture)
                picture_box.set_reactive(True)
                group.add_child(picture_box)
            except GLib.GError, e:
                print >> sys.stderr, 'Error loading image', e

        self.gtmap.show_popup(self, group)

        self._visible = True

    def hide(self):
        self.gtmap.unshow_popup(self)
            
        self._visible = False
