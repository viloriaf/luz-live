#!/usr/bin/env python

import gtk
import gtk.glade
import gobject

class GladeHandlers:

    def on_window1_destroy_event(widget, data=None):
        gtk.main_quit()

    def on_window1_delete_event(widget, event, data=None):
        gtk.main_quit()

    def on_potar_value_changed(widget,data=None):
        widgets["potar value"].set_label( str(int(widgets["potar"].get_value() * 100 / 255))+" %")
        
    def on_listePotars_cursor_changed():
    	pass


class WidgetsWrapper:
    def __init__(self):
        self.widgets = gtk.glade.XML("luz-live.glade")
        self.widgets.signal_autoconnect(GladeHandlers.__dict__)

        self.liststore = gtk.ListStore(gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_STRING)
        for i in range(512):
			self.liststore.append([i,'ligne '+str(i),'0 %'])
        self["listePotars"].set_model(self.liststore)
        
        number_column = gtk.TreeViewColumn('Numero de ligne')
        name_column = gtk.TreeViewColumn('Description')
        value_column = gtk.TreeViewColumn('Valeur')
        self["listePotars"].append_column(number_column)
        self["listePotars"].append_column(name_column)
        self["listePotars"].append_column(value_column)
        
        number_cell = gtk.CellRendererText()
        number_column.pack_start(number_cell)
        number_column.add_attribute(number_cell, 'text', 0)
        
        name_cell = gtk.CellRendererText()
        name_cell.set_property('editable', True)
        name_cell.connect('edited', self.change_name)
        name_column.pack_start(name_cell)
        name_column.add_attribute(name_cell,'text',1)
        
        value_cell = gtk.CellRendererText()
        value_column.pack_start(value_cell)
        value_column.add_attribute(value_cell,'text',2)

    def __getitem__(self, key):
        return self.widgets.get_widget(key)
        
    def change_name(self, cell, path, new_text):
        self.liststore[path][1]= new_text


if __name__ == "__main__":
    widgets = WidgetsWrapper()
    gtk.main()
