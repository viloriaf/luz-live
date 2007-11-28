#!/usr/bin/env python

import gtk
import gtk.glade

class GladeHandlers:

    def on_window1_destroy_event(widget, data=None):
        print "destroy"
        print widget
        print data
        gtk.main_quit()

    def on_window1_delete_event(widget, event, data=None):
        print "delete"
        print widget
        print event
        print data
        gtk.main_quit()

    def on_potar_value_changed(widget,data=None):
        widgets["potar value"].set_label( str(int(widgets["potar"].get_value() * 100 / 255))+" %")


class WidgetsWrapper:
    def __init__(self):
        self.widgets = gtk.glade.XML("luz-live.glade")
        self.widgets.signal_autoconnect(GladeHandlers.__dict__)

        liststore = gtk.ListStore(gobject.TYPE_INT,gobject.TYPE_STRING)

    def __getitem__(self, key):
        return self.widgets.get_widget(key)

if __name__ == "__main__":
    widgets = WidgetsWrapper()

    gtk.main()
