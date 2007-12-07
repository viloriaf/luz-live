#!/usr/bin/env python

import gtk
import gtk.glade
import gobject

class GladeHandlers:

    def on_window1_destroy_event(widget, data=None):
        gtk.main_quit()

    def on_window1_delete_event(widget, event, data=None):
        gtk.main_quit()

    def on_potarValueActual_value_changed(widget,data=None):
        new_value_str = str(int(widgets["potarValueActual"].get_value() * 100 / 255))+" %"
        widgets["labelPotarValue"].set_label(new_value_str)
        
        path = widgets["listPotar"].get_cursor()[0][0]
        widgets.liststore[path][2]=new_value_str 
        widgets.liststore[path][3]=widgets["potarValueActual"].get_value()
		
    def on_listPotar_cursor_changed(treeview):
    	path = treeview.get_cursor()[0][0]
    	##print widgets.liststore[path][0]
    	
    	##print widgets.liststore[path][2]
        widgets["potarValueActual"].set_value(widgets.liststore[path][3])
        widgets["labelPotarName"].set_label(widgets.liststore[path][1])
    	
class WidgetsWrapper:
    def __init__(self):
        self.widgets = gtk.glade.XML("luz-live.glade")
        self.widgets.signal_autoconnect(GladeHandlers.__dict__)

        self.liststore = gtk.ListStore(gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_INT)
        for i in range(512):
			self.liststore.append([i,'ligne '+str(i),'0 %',0])
        self["listPotar"].set_model(self.liststore)
        
        number_column = gtk.TreeViewColumn('Numero de ligne')
        name_column = gtk.TreeViewColumn('Description')
        value_column = gtk.TreeViewColumn('Valeur')
        self["listPotar"].append_column(number_column)
        self["listPotar"].append_column(name_column)
        self["listPotar"].append_column(value_column)
        
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
        widgets["labelPotarName"].set_label(new_text)

if __name__ == "__main__":
    widgets = WidgetsWrapper()
    widgets["listPotar"].set_cursor(0)
    gtk.main()
