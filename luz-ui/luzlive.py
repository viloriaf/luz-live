#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gtk.glade
import gobject

# import xml.dom.minidom
# from xml.dom.ext import PrettyPrint

import os.path

try:
    import lla
    import_lla = True
except: 
    import_lla = False

class Effect:

    def __init__(self,liststore):
        self.channels={}
        self.submasters={}

        if type(liststore)==listPotar:
            iter = liststore.iter_children(liststore.iter_potars)
            while iter :
                self.channels[liststore.get_value(iter,0)]=liststore.get_value(iter,3)
                iter = liststore.iter_next(iter)

            iter = liststore.iter_children(liststore.iter_submasters)
            while iter:
                self.submasters[liststore.get_value(iter,0)]=liststore.get_value(iter,3)
                iter = liststore.iter_next(iter)
            ##for row in liststore. :
            ##    self.channels[row[0]]=row[3]
        elif type(liststore)==xml.dom.minicompat.NodeList:
            for i in range(len(widgets.liststore)):
                self.channels[i]=0
            ##TODO : idem piour les submasters
            for channel in liststore:
                self.channels[int(channel.getAttribute("id"))]=int(channel.getAttribute("value"))
            for submaster in liststore:
                self.submasters[int(submaster.getAttribute("id"))]=int(submaster.getAttribute("value"))

    def getXml(self, doc, effectNode):
        for channel_id,value in self.channels.items():
            if value>0:
                channel = doc.createElement("channel")
                channel.setAttribute("id",str(channel_id))
                channel.setAttribute("value",str(value))
                effectNode.appendChild(channel)
        for submaster_id,value in self.submasters.items():
            if value>0:
                submaster = doc.createElement("submaster")
                submaster.setAttribute("id",str(submaster_id))
                submaster.setAttribute("value",str(value))
                effectNode.appendChild(submaster)

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

    def add(self,listPotars):
        num_item=len(self)+1
        self.append([
            num_item,
            "Effect "+str(num_item),
            Effect(listPotars)
        ])

    def modify(self,path,listPotars):
        self[path][2] = Effect(listPotars)

    def remove(self,path):
        gtk.ListStore.remove(self,self.get_iter(path))
        self.recount_all()

    def recount_all(self):
        for i in range(len(self)):
            self[i][0]=i+1

class listPotar(gtk.TreeStore):
    def __init__(self):
        gtk.TreeStore.__init__(self,
            gobject.TYPE_STRING, ## 0 - numéro de la ligne
            gobject.TYPE_STRING, ## 1 - nom de la ligne
            gobject.TYPE_STRING, ## 2 - valeur de la ligne en pourcentage
            gobject.TYPE_INT)    ## 3 - valeur de la ligne <255
        self.iter_submasters = self.append(None,["","SubMasters","",0])
        self.iter_potars = self.append(None,["","Lignes","",0])
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

    def getLine(self, path):
        return self[path]

    def getPotar(self,id):
        iter = self.iter_nth_child(self.iter_potars, id-1)
        path = self.get_path(iter)
        return self[path]

    def getSubMaster(self,id):
        iter = self.iter_nth_child(self.iter_submasters, id-1)
        path = self.get_path(iter)
        return self[path]

    def getDmxBuffer(self):
        dmxBuffer = lla.dmxBuffer(widgets.DMX_LEN)
        tmpBuffer={}
        iter = self.iter_children(self.iter_potars)
        while iter :
            path = self.get_path(iter)
            ##print "path"+str(path[1])
            ##print 'value'+str(self[path][3])
            dmxBuffer[path[1]]=self[path][3]
            tmpBuffer[path[1]]=self[path][3]
            iter = self.iter_next(iter)

        iter = self.iter_children(self.iter_submasters)
        while iter:
            submaster_value = self.get_value(iter, 3)
            iter_children=self.iter_children(iter)
            while iter_children:
                line_id=int(self.get_value(iter_children,0))
                line_value=self.get_value(iter_children,3)
                ##print line_id, type(line_id)
                ##print line_value, type(line_value)
                dmxBuffer[line_id]=max(tmpBuffer[line_id],line_value*submaster_value/255)
                if line_id==1:
                    print tmpBuffer[line_id], line_value*submaster_value/255
                iter_children=self.iter_next(iter_children)
            iter=self.iter_next(iter)
        return dmxBuffer

    def addSubMaster(self):
        number = self.iter_n_children(self.iter_submasters)+1
        new_iter = self.append(self.iter_submasters,[number,'Submaster '+str(number),'0 %',0])
        iter = self.iter_children(self.iter_potars)
        got_one = False
        while iter :
            path = self.get_path(iter)
            if self[path][3]*100/255!=0:
                got_one=True
                self.append(new_iter,self[path])

            iter = self.iter_next(iter)
        if not got_one:
            self.remove(new_iter)


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
        widgets.effects_liststore.add(widgets.liststore)

    def on_buttonModifyEffect_clicked(toolbutton):
        print "buttonModifyEffect"
        path = widgets["listEffect"].get_cursor()[0][0]

        widgets.effects_liststore.modify(path,widgets.liststore)

        cursor_path = widgets["listPotar"].get_cursor()[0]
        if len(cursor_path)>1:
            widgets["potarValueMemory"].set_value(widgets.liststore.getLine(cursor_path)[3])
        ## si on est dans les submasters
        # if [0]==0:
            # pass
        # si on est dans les lignes
        # elif widgets["listPotar"].get_cursor()[0][0]==1:
            # if len(widgets["listPotar"].get_cursor()[0])>1:
                # path = widgets["listPotar"].get_cursor()[0][1]+1
                

    def on_buttonDeleteEffect_clicked(toolbutton):
        print "buttonDeleteEffect"
        path = widgets["listEffect"].get_cursor()[0]
        widgets.effects_liststore.remove(path)

        widgets["buttonModifyEffect"].set_sensitive(False)
        widgets["buttonDeleteEffect"].set_sensitive(False)


    def on_buttonAddSubmaster_clicked(toolbutton):
        print "buttonAddSubmaster"
        widgets.liststore.addSubMaster()
        widgets["listPotar"].expand_row((0,), False)

    def on_buttonDeleteSubmaster_clicked(tollbutton):
        print "buttonDeleteSubmaster"

    ###################################################################
    ## Fenêtre principal                                              #
    ###################################################################
    def on_potarValueActual_value_changed(widget,data=None):
        new_value_str = str(int(widgets["potarValueActual"].get_value() * 100 / 255))+" %"
        widgets["labelPotarValue"].set_label(new_value_str)

        ## si on est dans les submasters
        ##if len(widgets["listPotar"].get_cursor()[0])>1:
        ##    if widgets["listPotar"].get_cursor()[0][0]==0:
        ##        path = widgets["listPotar"].get_cursor()[0][1]+1
        ##        widgets.liststore.getSubMaster(path)[2]=new_value_str
        ##        widgets.liststore.getSubMaster(path)[3]=widgets["potarValueActual"].get_value()
            ## si on est dans les lignes
        ##    elif widgets["listPotar"].get_cursor()[0][0]==1:
        ##        path = widgets["listPotar"].get_cursor()[0][1]+1
        ##        widgets.liststore.getPotar(path)[2]=new_value_str
        ##        widgets.liststore.getPotar(path)[3]=widgets["potarValueActual"].get_value()

        path = widgets["listPotar"].get_cursor()[0]
        if len(path)>1:
            widgets.liststore.getLine(path)[2]=new_value_str
            widgets.liststore.getLine(path)[3]=widgets["potarValueActual"].get_value()
        else:
            widgets.liststore.getLine(last)[2]=new_value_str
            widgets.liststore.getLine(last)[3]=widgets["potarValueActual"].get_value()

        ##print "on_potarValueActual_value_changed"
        ##widgets.sendDMX()

    def on_listPotar_cursor_changed(treeview):
        ##if len(treeview.get_cursor()[0])>1:
        path = treeview.get_cursor()[0]
        if len(path)>1:
            last_potar = path

            widgets["potarValueActual"].set_value(widgets.liststore.getLine(path)[3])
            if path[0]==0 and len(path)==3:
                new_label="SubMaster "+str(path[1]+1)+" : "+widgets.liststore.getLine(path)[1]
            else:
                new_label=widgets.liststore.getLine(path)[1]
            widgets["labelPotarName"].set_label(new_label)

        ## si on est dans les submasters
        ##if treeview.get_cursor()[0][0]==0:
        ##    if len(treeview.get_cursor()[0])==2:
        ##        path = treeview.get_cursor()[0][1]+1
        ##        widgets["potarValueActual"].set_value(widgets.liststore.getSubMaster(path)[3])
        ##        widgets["labelPotarName"].set_label(widgets.liststore.getSubMaster(path)[1])
        ##    elif len(treeview.get_cursor()[0])==3:
        ##        pass
        ## si on est dans les lignes
        ##elif treeview.get_cursor()[0][0]==1:
        ##    if len(treeview.get_cursor()[0])>1:
        ##        path = treeview.get_cursor()[0][1]+1
        ##        widgets["potarValueActual"].set_value(widgets.liststore.getPotar(path)[3])
        ##        widgets["labelPotarName"].set_label(widgets.liststore.getPotar(path)[1])

    def on_listEffect_cursor_changed(treeview):
        path = treeview.get_cursor()[0][0]
        effect_to_put = widgets.effects_liststore[path][2]

        for nchannel,value in effect_to_put.channels.items():
            widgets.liststore.getPotar(int(nchannel))[3]=value
            widgets.liststore.getPotar(int(nchannel))[2]=str(value*100/255)+" %"
        for nsub,value in effect_to_put.submasters.items():
            widgets.liststore.getSubMaster(int(nsub))[3]=value
            widgets.liststore.getSubMaster(int(nsub))[2]=str(value*100/255)+" %"

        cursor_path = widgets["listPotar"].get_cursor()[0]
        if len(cursor_path)>1:
            widgets["potarValueActual"].set_value(widgets.liststore.getLine(cursor_path)[3])
            widgets["potarValueMemory"].set_value(widgets.liststore.getLine(cursor_path)[3])
            widgets["labelPotarName"].set_label(widgets.liststore.getLine(cursor_path)[1])
            
            
        # if widgets["listPotar"].get_cursor()[0][0]==0:
            # pass
        # elif widgets["listPotar"].get_cursor()[0][0]==1:
            # if len(widgets["listPotar"].get_cursor()[0])>1:
                # path = widgets["listPotar"].get_cursor()[0][0]
                # widgets["potarValueActual"].set_value(widgets.liststore.getPotar(path)[3])
                # widgets["potarValueMemory"].set_value(widgets.liststore.getPotar(path)[3])

                # widgets["labelPotarName"].set_label(widgets.liststore.getPotar(path)[1])

        widgets["buttonModifyEffect"].set_sensitive(True)
        widgets["buttonDeleteEffect"].set_sensitive(True)

    def on_listEffect_drag_begin(widget, drag_context):
        widgets["buttonAddEffect"].set_sensitive(False)

    def on_listEffect_drag_end(widget, drag_context):
        for i in range(len(widgets.effects_liststore)):
            widgets.effects_liststore[i][0] = i+1

class WidgetsWrapper:

    ###################################################################
    ## Fonctions d'init                                               #
    ###################################################################
    def __init__(self):
        self.widgets = gtk.glade.XML("luz-live.glade")
        self.widgets.signal_autoconnect(GladeHandlers.__dict__)
        self.init_DMX()
        self.init_effects()
        self.init_filechooser()

        self.filename = ""

        self.init_LLA()

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
        value_cell.set_property('editable', True)
        value_cell.connect('edited', self.change_value)
        value_column.pack_start(value_cell)
        value_column.set_cell_data_func(value_cell,self.display_value_cell)

        self["listPotar"].set_expander_column(name_column)
        ##value_column.add_attribute(value_cell,'text',2)

        self["listPotar"].expand_all()

        self.liststore.connect("row-changed", self.on_listPotar_rowchanged)

    def init_LLA(self):
        if import_lla:
            self.con = lla.LlaClient()
            if self.con.start():
                self.con_success = False
                print "Connexion échoué à LLAD"
            else:
                self.con_success = True
            self.universe = 0
            self.DMX_LEN = 512
        else:
            self.con_success = False
            
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

    ###################################################################
    ## Callbacks                                                      #
    ###################################################################
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

    def change_name(self, cell, path, new_text):
        self.liststore[path][1]= new_text
        widgets["labelPotarName"].set_label(new_text)

    def change_value(self,cell, path, new_text):
        if new_text.isalnum() and not new_text.isalpha():
            new_value=int(new_text)
        elif new_text[-2:]==' %' and new_text[:-2].isalnum() and not new_text[:-2].isalpha():
            new_value=int(new_text[:-2])
        elif new_text[-1]=='%' and new_text[:-1].isalnum() and not new_text[:-1].isalpha():
            new_value=int(new_text[:-1])

        if new_value>100:
            new_value=100
        elif new_value<0:
            new_value=0
        self.liststore[path][2]=str(new_value)+" %"
        self.liststore[path][3]=new_value*255/100+1

    def on_listPotar_rowchanged(self, treemodel, path, iter):
        self.sendDMX()

    def change_desc_effect(self, cell, path, new_text):
        self.effects_liststore[path][1]=new_text

    def display_effect(self, column, cell, model, iter, user_data):
        effect = model.get_value(iter, 1)
        cell.set_property('text', str(effect))
        return

    ###################################################################
    ## Divers                                                         #
    ###################################################################
    def __getitem__(self, key):
        return self.widgets.get_widget(key)

    def sendDMX(self):
        ##print "sendDMX"
        if self.con_success:
            buffer = self.liststore.getDmxBuffer()
            self.con.send_dmx(self.universe,buffer,self.DMX_LEN)

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
    last=(1,0)
    ##widgets['listPotar'].set_cursor(widgets.liststore.get_path(widgets.liststore.iter_children(widgets.liststore.iter_potars)))
    widgets['listPotar'].set_cursor(last)
    gtk.main()
