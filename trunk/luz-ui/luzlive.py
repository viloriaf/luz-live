#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gtk.glade
import gobject

class Effect:

    def __init__(self,liststore):
        self.desc=""
        self.channels={}
        
        for row in liststore :
            self.channels[row[0]]=row[3]

    def __str__(self):
        return self.desc
        
    def set_desc(self,new_text):
        self.desc = new_text
        
class listEffect(gtk.liststore):
    def __init__(self):
        gtk.liststore.__init__(self, gobject.TYPE_INT, gobject.TYPE_PYOBJECT)
    
    def getXmlNode(self):
        pass
    
class listPotar(gtk.liststore):
    def __init__(self):
        gtk.ListStore.__init__(self,gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_INT)
        for i in range(512):
            self.append([i+1,'ligne '+str(i+1),'0 %',0])

    def getXmlNode(self):
        pass

class GladeHandlers:

    def on_window1_destroy_event(widget, data=None):
        gtk.main_quit()

    def on_window1_delete_event(widget, event, data=None):
        gtk.main_quit()

    def on_menu_quit_activate(menuitem):
        gtk.main_quit()

    def on_potarValueActual_value_changed(widget,data=None):
        new_value_str = str(int(widgets["potarValueActual"].get_value() * 100 / 255))+" %"
        widgets["labelPotarValue"].set_label(new_value_str)
        
        path = widgets["listPotar"].get_cursor()[0][0]
        widgets.liststore[path][2]=new_value_str 
        widgets.liststore[path][3]=widgets["potarValueActual"].get_value()
        
    def on_listPotar_cursor_changed(treeview):
        path = treeview.get_cursor()[0][0]
        widgets["potarValueActual"].set_value(widgets.liststore[path][3])
        widgets["labelPotarName"].set_label(widgets.liststore[path][1])
        
    def on_listEffect_cursor_changed(treeview):
        path = treeview.get_cursor()[0][0]
        effect_to_put = widgets.effects_liststore[path][1]
        for nchannel,value in effect_to_put.channels.items():
            widgets.liststore[nchannel-1][3]=value
            widgets.liststore[nchannel-1][2]=str(value*100/255)+" %"
            
        path = widgets["listPotar"].get_cursor()[0][0]
        widgets["potarValueActual"].set_value(widgets.liststore[path][3])
        widgets["labelPotarName"].set_label(widgets.liststore[path][1])
        
        widgets["Enregistrer"].set_sensitive(True)
        
    def on_listEffect_drag_begin(widget, drag_context):
        widgets["Enregistrer"].set_sensitive(False)
                
    def on_listEffect_drag_end(widget, drag_context):
        for i in range(len(widgets.effects_liststore)):
            widgets.effects_liststore[i][0] = i+1
        
    def on_enregistrernouveau_clicked(toolbutton):
        widgets.effects_liststore.append([len(widgets.effects_liststore)+1,Effect(widgets.liststore)])
        
    def on_Enregistrer_clicked(toolbutton):
        path = widgets["listEffect"].get_cursor()[0][0]
        widgets.effects_liststore[path][1] = Effect(widgets.liststore)

class WidgetsWrapper:
    def __init__(self):
        self.widgets = gtk.glade.XML("luz-live.glade")
        self.widgets.signal_autoconnect(GladeHandlers.__dict__)
        self.init_DMX()
        self.init_effects()
        
    def init_DMX(self):
        self.liststore = listPotar()
            
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
        
    def init_effects(self):
        self.effects_liststore = listEffects()
        
        self["listEffect"].set_model(self.effects_liststore)
        
        number_column_effect = gtk.TreeViewColumn("Numero de l'effet")
        desc_column_effect = gtk.TreeViewColumn("Description de l'effet")
        
        self["listEffect"].append_column(number_column_effect)
        self["listEffect"].append_column(desc_column_effect)
        
        number_effect_cell = gtk.CellRendererText()
        number_column_effect.pack_start(number_effect_cell)
        number_column_effect.add_attribute(number_effect_cell,'text',0)
        
        desc_effect_cell = gtk.CellRendererText()
        desc_effect_cell.set_property('editable', True)
        desc_effect_cell.connect('edited', self.change_desc_effect)
        desc_column_effect.pack_start(desc_effect_cell)
        desc_column_effect.set_cell_data_func(desc_effect_cell, self.display_effect, None)
            
    def __getitem__(self, key):
        return self.widgets.get_widget(key)
        
    def change_name(self, cell, path, new_text):
        self.liststore[path][1]= new_text
        widgets["labelPotarName"].set_label(new_text)
        
    def change_desc_effect(self, cell, path, new_text):
        self.effects_liststore[path][1].set_desc(new_text)

    def display_effect(self, column, cell, model, iter, user_data):
        pyobj = model.get_value(iter, 1)
        cell.set_property('text', str(pyobj))
        return

if __name__ == "__main__":
    widgets = WidgetsWrapper()
    widgets["listPotar"].set_cursor(0)
    gtk.main()
