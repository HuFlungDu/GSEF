from gi.repository import GtkClutter as cluttergtk #@UnresolvedImport   # must be the first to be imported
from gi.repository import Clutter as clutter #@UnresolvedImport
from gi.repository import Gtk, Gdk #@UnresolvedImport
import sys
import Globals#@UnresolvedImport
from Popups import ConfirmationDialog
import shutil

class SystemsTreeView(Gtk.TreeView):
    def __init__(self,treestore):
        Gtk.TreeView.__init__(self,treestore)
        tvcolumn = Gtk.TreeViewColumn('System')
        tvcolumn2 = Gtk.TreeViewColumn('Core')
        self.append_column(tvcolumn)
        self.append_column(tvcolumn2)
        cell = Gtk.CellRendererText()
        cell2 = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, False)
        tvcolumn2.pack_start(cell2, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        tvcolumn2.add_attribute(cell2, 'text', 1)
    
    def get_selected_strings(self):
        (treemodel, treeiter) = self.get_selection().get_selected()
        return treemodel.get(treeiter,0,1)
    
    def get_selected_parent_strings(self):
        (treemodel, treeiter) = self.get_selection().get_selected()
        parentiter = treemodel.iter_parent(treeiter)
        return treemodel.get(parentiter,0,1)
        
        
        

class ManageSystemsWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Manage Systems And Cores")
        Globals.OpenWindows |= Globals.WINDOWTYPE_MANAGESYSTEMS
        mainvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_default_size(500,500)
        #generateTreeStore(ControlData, self.treestore)
        treeview = SystemsTreeView(self.make_treestore())
        removebutton = Gtk.Button("Remove")
        removebutton.set_sensitive(False)
        treeview.get_selection().connect("changed", self.tvchanged, removebutton)
        removebutton.connect("clicked",self.removesys,treeview)
        
        donebutton = Gtk.Button("Done")
        donebutton.connect("clicked",self.Destroy_Window)
        mainvbox.pack_start(treeview, True, True, 0)
        mainhbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        mainhbox.pack_end(donebutton, False, False, 10)
        mainhbox.pack_end(removebutton, False, False, 5)
        
        self.connect("delete-event",self.On_Delete)
        mainvbox.pack_start(mainhbox,False,False,10)
        self.add(mainvbox)
    
    def Destroy_Window(self,widget1):
        self.destroy()
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_MANAGESYSTEMS
        
    def On_Delete(self,Window,ResponseType):
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_MANAGESYSTEMS
    
    def make_treestore(self):
        systemsdic = {}
        for i in Globals.Systems:
            coreslist = []
            for j in Globals.Cores:
                core = j.split("/")
                if core[0] == i:
                    coreslist.append(core[1])
            systemsdic[i] = coreslist
            
        treestore = Gtk.TreeStore(str,str)
        for i in systemsdic:
            parent = treestore.append(None, [i,""])
            for j in systemsdic[i]:
                treestore.append(parent,["",j])
        return treestore
    
    def removesys(self,Button,Treeview):
        (SysString, CoreString) = Treeview.get_selected_strings()
        if not SysString:
            dialog = ConfirmationDialog("Remove Core", "Remove this core?")
            dialog.connect("response",self.ConfirmationReturn,Treeview)
            dialog.set_transient_for(self)
            dialog.show_all()
        else:
            dialog = ConfirmationDialog("Remove System", "Remove this system and all it's cores?")
            dialog.connect("response",self.ConfirmationReturn,Treeview)
            dialog.set_transient_for(self)
            dialog.show_all()
    
    def ConfirmationReturn(self,window,ResponseType,Treeview):
        if ResponseType == Gtk.ResponseType.ACCEPT:
            (SysString, CoreString) = Treeview.get_selected_strings()
            if not SysString:
                SysString = Treeview.get_selected_parent_strings()[0]
                shutil.rmtree(Globals.DataDir+"Systems/"+"System_"+SysString+"/Core_"+CoreString)
                Globals.Cores.remove(SysString+"/"+CoreString)
            else:
                shutil.rmtree(Globals.DataDir+"Systems/"+"System_"+SysString)
                Globals.Systems.remove(SysString)
                CoreRems = []
                for i in Globals.Cores:
                    if i.split("/")[0] == SysString:
                        CoreRems.append(i)
                for i in CoreRems:
                    Globals.Cores.remove(i)
            Treeview.set_model(self.make_treestore())
                        
                
        #print Selection
        window.destroy()
    
    def tvchanged(self, Selection,removebutton):
        #if Selection
        if Selection.get_selected()[1]:
            removebutton.set_sensitive(True)
        else:
            removebutton.set_sensitive(False)
        #print Selection.get_data()
        #print Selection
        #print Selection.get_selected()[0].get(Selection.get_selected()[1],0)