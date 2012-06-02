from gi.repository import GtkClutter as cluttergtk #@UnresolvedImport   # must be the first to be imported
from gi.repository import Gtk, Gdk #@UnresolvedImport
from gi.repository import Clutter as clutter #@UnresolvedImport
from gi.repository import Cogl as cogl #@UnresolvedImport

import os
import shutil

from Popups import ErrorPopupWindow #@UnresolvedImport
import xml.etree.ElementTree as ET
from CompressionWrapper import Archive#@UnresolvedImport
import Globals#@UnresolvedImport
from Popups import ConfirmationDialog

class GamesTreeView(Gtk.TreeView):
    def __init__(self,treestore):
        Gtk.TreeView.__init__(self,treestore)
        tvcolumn = Gtk.TreeViewColumn('')
        self.append_column(tvcolumn)
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, False)
        tvcolumn.add_attribute(cell, 'text', 0)
    
    def get_selected_strings(self):
        (treemodel, treeiter) = self.get_selection().get_selected()
        return treemodel.get(treeiter,0)
    
    def get_selected_parent_strings(self):
        (treemodel, treeiter) = self.get_selection().get_selected()
        parentiter = treemodel.iter_parent(treeiter)
        return treemodel.get(parentiter,0)
    
    def get_selection_tree_strings(self):
        (model, pathlist) = self.get_selection().get_selected_rows()
        path = pathlist[0]
        tree_iter = model.get_iter(path)
        value = model.get_value(tree_iter,0)
        tree = [value]
        while path.up() and path.get_depth():
            tree_iter = model.get_iter(path)
            value = model.get_value(tree_iter,0)
            tree.insert(0,value)
        while len(tree) < 3:
            tree.append(u"")
        return tree
        

class ManageGamesWindow(Gtk.Window):
    def __init__(self):
        Globals.OpenWindows |= Globals.WINDOWTYPE_MANAGEGAMES
        Gtk.Window.__init__(self,title="Manage games")
        mainvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_default_size(500,500)
        treeview = GamesTreeView(self.make_treestore())
        removebutton = Gtk.Button("Remove")
        removebutton.set_sensitive(False)
        playbutton = Gtk.Button("Play Game")
        playbutton.set_sensitive(False)
        treeview.get_selection().connect("changed", self.tvchanged, removebutton, playbutton)
        removebutton.connect("clicked",self.removegame,treeview)
        playbutton.connect("clicked", self.playgame, treeview)
        donebutton = Gtk.Button("Done")
        donebutton.connect("clicked",self.Destroy_Window)
        mainvbox.pack_start(treeview, True, True, 0)
        mainhbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        mainhbox.pack_end(donebutton, False, False, 10)
        mainhbox.pack_end(playbutton, False, False, 5)
        mainhbox.pack_end(removebutton, False, False, 5)
        treeview.connect("row-activated", self.playgametv)
        
        self.connect("delete-event",self.On_Delete)
        mainvbox.pack_start(mainhbox,False,False,10)
        self.add(mainvbox)
        
        
    def Destroy_Window(self,widget1):
        self.destroy()
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_MANAGEGAMES
        
    def On_Delete(self,Window,ResponseType):
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_MANAGEGAMES
        
    def make_treestore(self):            
        treestore = Gtk.TreeStore(str)
        for i in Globals.Games:
            parent = treestore.append(None, [i])
            for j in Globals.Games[i]:
                parent2 = treestore.append(parent,[j.name])
                for k in Globals.Games[i][j]:
                    treestore.append(parent2,[k])
        return treestore
    
    def playgametv(self,Treeview, Path, Column):
        (_, pathlist) = Treeview.get_selection().get_selected_rows()
        if len(pathlist) and pathlist[0].get_depth()>1:
            self.playgame(None,Treeview)
        
    
    def removegame(self,Button,Treeview):
        (_, pathlist) = Treeview.get_selection().get_selected_rows()
        depth = pathlist[0].get_depth()
        if depth == 3:
            dialog = ConfirmationDialog("Remove Patch", "Remove this patch and all its data?")
            dialog.connect("response",self.ConfirmationReturn,Treeview)
            dialog.set_transient_for(self)
            dialog.show_all()
        elif depth == 2:
            dialog = ConfirmationDialog("Remove Game", "Remove this game and all its data?")
            dialog.connect("response",self.ConfirmationReturn,Treeview)
            dialog.set_transient_for(self)
            dialog.show_all()
    
    def playgame(self,Button,Treeview):
        (_, pathlist) = Treeview.get_selection().get_selected_rows()
        depth = pathlist[0].get_depth()
        tree = Treeview.get_selection_tree_strings()
        Sysname, Gamename, Patchname = tree[0],tree[1],tree[2]
        corename = filter(lambda x: x.name == Gamename,Globals.Games[Sysname].keys())[0].core
        Globals.load_game(Sysname, corename, Gamename, Patchname)
        self.Destroy_Window(self)
        
        
    def ConfirmationReturn(self,window,ResponseType,Treeview):
        if ResponseType == Gtk.ResponseType.ACCEPT:
            (_, pathlist) = Treeview.get_selection().get_selected_rows()
            path = pathlist[0]
            depth = path.get_depth()
            tree = Treeview.get_selection_tree_strings()
            Sysname, Gamename, Patchname = tree[0],tree[1],tree[2]
            Syslam = lambda x: x.get("name") == Sysname
            Gamelam = lambda x: x.get("name") == Gamename
            Patchlam = lambda x: x.get("name") == Patchname 
            if depth == 3:
                for i in filter(Syslam, Globals.GamesXML.findall("System")):
                    for j in filter(Gamelam, i.findall("Game")):
                        for k in filter(Patchlam, j.findall("Patch")):
                            j.remove(k)
                shutil.rmtree(Globals.DataDir+"Games/"+Sysname+"/"+Gamename+"/"+Patchname)
            elif depth == 2:
                shutil.rmtree(Globals.DataDir+"Games/"+Sysname+"/"+Gamename)
                for i in filter(Syslam, Globals.GamesXML.findall("System")):
                    for j in filter(Gamelam, i.findall("Game")):
                        i.remove(j)
            Globals.Update_Games()
            Treeview.set_model(self.make_treestore())
            
        self.Destroy_Window(self)
    
    def tvchanged(self, Selection,removebutton,playbutton):
        (_, pathlist) = Selection.get_selected_rows()
        if len(pathlist) and pathlist[0].get_depth()>1:
            removebutton.set_sensitive(True)
            playbutton.set_sensitive(True)
        else:
            removebutton.set_sensitive(False)
            playbutton.set_sensitive(False)