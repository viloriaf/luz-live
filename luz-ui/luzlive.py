#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gtk.glade
import gobject

import xml.dom.minidom
from xml.dom.ext import PrettyPrint

import os.path

class Effect:

    def __init__(self,liststore):
        self.channels={}
        
        if type(liststore)==listPotar:
            for row in liststore : 
                self.channels[row[0]]=row[3]
        elif type(liststore)==xml.dom.minicompat.NodeList:
            for i in range(len(widgets.liststore)):
                self.channels[i]=0
            for channel in liststore:
                self.channels[int(channel.getAttribute("id"))]=int(channel.getAttribute("value"))

    def getXml(self, doc, effectNode):
        for channel_id,value in self.channels.items():
            if value>0:
                channel = doc.createElement("channel")
                channel.setAttribute("id",str(channel_id))
                channel.setAttribute("value",str(value))
                effectNode.appendChild(channel)

class listEffect(gtk.ListStore):
    def __init__(self):
        gtk.ListStore.__init__(self, gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
    
    def getXml(self,doc,root):
        effectListNode=doc.createElement("listEffect")
        for effect_id,effect_desc,effect in self:
            effectNode = doc.createElement("effect")
            effectNode.setAttribute("id",str(effect_id))
            effectNode.setAttribute("desc",str(effect_desc))
            effect.getXml(doc,effectNode)
            effectListNode.appendChild(effectNode)
        root.appendChild(effectListNode)
        
    def setXml(self,listEffectNode):
        self.clear()
        for effect in listEffectNode.getElementsByTagName("effect"):
            effect_obj = Effect(effect.getElementsByTagName("channel"))
            self.append([int(effect.getAttribute("id")),effect.getAttribute("desc"),effect_obj])

class listPotar(gtk.TreeStore):
    def __init__(self):
        gtk.TreeStore.__init__(self,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_INT)
        self.iter_submasters = self.append(None,["","SubMasters","0 %",0])
        self.iter_potars = self.append(None,["","Lignes","0 %",0])
        for i in range(512):
            self.append(self.iter_potars,[str(i+1),'Ligne '+str(i+1),'0 %',0])

    def getXml(self,doc,root):
        device = doc.createElement("device")
        for line_id, line_desc, line_percent, line_value in self:
            line = doc.createElement("line")
            line.setAttribute("id",str(line_id))
            line.setAttribute("desc",str(line_desc))
            device.appendChild(line)
        root.appendChild(device)
        
    def setXml(self,deviceNode):
        self.clear()
        for line in deviceNode.getElementsByTagName("line"):
            self.append( [
                int(line.getAttribute("id")),
                line.getAttribute("desc"),
                '0 %', 0 ] )

class GladeHandlers:

	###################################################################
	## General                                                        #
    ###################################################################
    def on_window1_destroy_event(widget, data=None):
        gtk.main_quit()

    def on_window1_delete_event(widget, event, data=None):
        gtk.main_quit()

	###################################################################
	## Menu                                                           #
	###################################################################
    def on_Quit_activate(menuitem):
        gtk.main_quit()
        
    def on_About_activate(menuitem):
        widgets["aboutdialog1"].run()
        widgets["aboutdialog1"].hide()

	###################################################################
	## ToolBar                                                        #
	###################################################################
    def on_buttonOpenShow_clicked(toolbutton):
    	print "buttonOpenShow"
        retour = widgets["filechooserdialog_open"].run()
        widgets["filechooserdialog_open"].hide()
        if retour == 0:
            widgets.load( widgets["filechooserdialog_open"].get_filename() )
        
    def on_buttonSaveShow_clicked(toolbutton):
        print "buttonSaveShow"
        if widgets.filename:
            widgets.save( widgets.filename )
        else:
            retour = widgets["filechooserdialog_save"].run()
            widgets["filechooserdialog_save"].hide()
            if retour == 0:
                widgets.save( widgets["filechooserdialog_save"].get_filename() )

    def on_buttonAddEffect_clicked(toolbutton):
    	print "buttonAddEffect"
        widgets.effects_liststore.append([len(widgets.effects_liststore)+1,"",Effect(widgets.liststore)])

    def on_buttonModifyEffect_clicked(toolbutton):
    	print "buttonModifyEffect"
        path = widgets["listEffect"].get_cursor()[0][0]
        widgets.effects_liststore[path][2] = Effect(widgets.liststore)

	def on_buttonDeleteEffect_clicked(toolbutton):
		print "buttonDeleteEffect"
		
	def on_buttonAddSubmaster_clicked(toolbutton):
		print "buttonAddSubmaster"
		
	def on_buttonModifySubmaster_clicked(toolbutton):
		print "buttonModifySubmaster"
		
	def on_buttonDeleteSubmaster_clicked(tollbutton):
		print "buttonDeleteSubmaster"

	###################################################################
	## Fenêtre principal                                              #
	###################################################################
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
        effect_to_put = widgets.effects_liststore[path][2]
        
        for nchannel,value in effect_to_put.channels.items():
            widgets.liststore[nchannel-1][3]=value
            widgets.liststore[nchannel-1][2]=str(value*100/255)+" %"
            
        path = widgets["listPotar"].get_cursor()[0][0]
        widgets["potarValueActual"].set_value(widgets.liststore[path][3])
        widgets["labelPotarName"].set_label(widgets.liststore[path][1])
        widgets["buttonModifyEffect"].set_sensitive(True)
        
    def on_listEffect_drag_begin(widget, drag_context):
        widgets["buttonAddEffect"].set_sensitive(False)
                
    def on_listEffect_drag_end(widget, drag_context):
        for i in range(len(widgets.effects_liststore)):
            widgets.effects_liststore[i][0] = i+1        

class WidgetsWrapper:
    def __init__(self):
        self.widgets = gtk.glade.XML("luz-live.glade")
        self.widgets.signal_autoconnect(GladeHandlers.__dict__)
        self.init_DMX()
        self.init_effects()
        self.init_filechooser()

        self.filename = ""

    def init_DMX(self):
        self.liststore = listPotar()
        self.potar_treemodelsort = gtk.TreeModelSort(self.liststore)
        self["listPotar"].set_model(self.potar_treemodelsort)
        
        number_column = gtk.TreeViewColumn('Numero de ligne')
        number_column.set_sort_column_id(0)
        name_column = gtk.TreeViewColumn('Description')
        name_column.set_sort_column_id(1)
        value_column = gtk.TreeViewColumn('Valeur')
        value_column.set_sort_column_id(2)
        self["listPotar"].append_column(number_column)
        self["listPotar"].append_column(name_column)
        self["listPotar"].append_column(value_column)
        
        number_cell = gtk.CellRendererText()
        number_column.pack_start(number_cell)
        number_column.set_cell_data_func(number_cell,self.display_number_cell)

        ##number_column.add_attribute(number_cell, 'text', 0)
        
        name_cell = gtk.CellRendererText()
        name_cell.set_property('editable', True)
        name_cell.connect('edited', self.change_name)
        name_column.pack_start(name_cell)
        name_column.add_attribute(name_cell,'text',1)
        
        value_cell = gtk.CellRendererText()
        value_column.pack_start(value_cell)
        value_column.set_cell_data_func(value_cell,self.display_value_cell)

        self["listPotar"].set_expander_column(name_column)
        ##value_column.add_attribute(value_cell,'text',2)
        
    def display_value_cell(self, column, cell, model, iter):
        if model[iter][0] > 0:
            cell.set_property('text', model.get_value(iter,2))
        else:
            cell.set_property('text', "")
        return
        
    def display_number_cell(self, column, cell, model, iter):
        if model[iter][0] > 0:
            cell.set_property('text', model.get_value(iter,0))
        else:
            cell.set_property('text', "")
        return
        
        
    def init_effects(self):
        self.effects_liststore = listEffect()
        self.effect_treemodelsort = gtk.TreeModelSort(self.effects_liststore)
        self["listEffect"].set_model(self.effect_treemodelsort)
        
        number_column_effect = gtk.TreeViewColumn("Numero de l'effet")
        number_column_effect.set_sort_column_id(0)
        desc_column_effect = gtk.TreeViewColumn("Description de l'effet")
        desc_column_effect.set_sort_column_id(1)
        
        self["listEffect"].append_column(number_column_effect)
        self["listEffect"].append_column(desc_column_effect)
        
        number_effect_cell = gtk.CellRendererText()
        number_column_effect.pack_start(number_effect_cell)
        number_column_effect.add_attribute(number_effect_cell,'text',0)
        
        desc_effect_cell = gtk.CellRendererText()
        desc_effect_cell.set_property('editable', True)
        desc_effect_cell.connect('edited', self.change_desc_effect)
        desc_column_effect.pack_start(desc_effect_cell)
        desc_column_effect.add_attribute(desc_effect_cell,'text',1)
            
    def init_filechooser(self):
        filter = gtk.FileFilter()
        filter.set_name("Luz Live file")
        filter.add_pattern("*.luz")
        self["filechooserdialog_save"].add_filter(filter)
        self["filechooserdialog_open"].add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        self["filechooserdialog_save"].add_filter(filter)

    def __getitem__(self, key):
        return self.widgets.get_widget(key)
        
    def change_name(self, cell, path, new_text):
        self.liststore[path][1]= new_text
        widgets["labelPotarName"].set_label(new_text)
        
    def change_desc_effect(self, cell, path, new_text):
        self.effects_liststore[path][1]=new_text

    def display_effect(self, column, cell, model, iter, user_data):
        pyobj = model.get_value(iter, 1)
        cell.set_property('text', str(pyobj))
        return
        
    def getXml(self):
        doc = xml.dom.minidom.Document()
        luz_root = doc.createElement("luz")
        self.liststore.getXml(doc,luz_root)
        self.effects_liststore.getXml(doc,luz_root)
        doc.appendChild(luz_root)
        return doc
        
    def save(self,filename):
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        basename, ext = os.path.splitext(basename)
        ext=".luz"
        filename = os.path.join(dirname,basename+ext)
        
        file = open(filename,"w")
        PrettyPrint(self.getXml(),file)
        file.close()
        
        self.filename = filename
        
    def load(self,filename):
        doc = xml.dom.minidom.parse(filename)
        self.liststore.setXml(doc.getElementsByTagName("device")[0])
        self.effects_liststore.setXml(doc.getElementsByTagName("listEffect")[0])
        
        self["listPotar"].set_cursor(0)
        self["listEffect"].set_cursor(0)
        
        self.filename = filename
        
        self.effect_treemodelsort.set_sort_column_id(0,gtk.SORT_ASCENDING)
        self.potar_treemodelsort.set_sort_column_id(0,gtk.SORT_ASCENDING)

if __name__ == "__main__":
    widgets = WidgetsWrapper()
    widgets['listPotar'].set_cursor(0)
    gtk.main()
