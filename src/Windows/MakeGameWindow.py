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

class MakeGameWindow(Gtk.Window):
    def __init__(self):
        Globals.OpenWindows |= Globals.WINDOWTYPE_MAKEGAME
        Gtk.Window.__init__(self,title="Create Game")
        mainvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_default_size(500,160)
        NameEntry = Gtk.Entry()
        NameEntry.set_text("Game name...")
        mainvbox.pack_start(NameEntry,False,True,5)
        #treestore = Gtk.TreeStore(str)
        syscorehbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        syscombobox = Gtk.ComboBoxText()
        for i in Globals.Systems:
            syscombobox.append_text(i)
        corecombobox = Gtk.ComboBoxText()
        corecombobox.set_sensitive(False)
        syscombobox.connect("changed",self.System_Box_Changed,corecombobox)
        
        syscorehbox.pack_start(syscombobox,True,True,5)
        syscorehbox.pack_start(corecombobox,True,True,5)
        mainvbox.pack_start(syscorehbox,False,False,5)
        
        filechooserbutton = Gtk.FileChooserButton()
        filechooserbutton.set_title("Game File")
        fcLabel = Gtk.Label("Game File:")
        fccheckbox = Gtk.CheckButton("Unpack File")
        fccheckbox.set_sensitive(False)
        filechooserbutton.connect("file-set",self.File_Selected,fccheckbox)
        fchbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        fchbox.pack_start(fcLabel,False,False,5)
        fchbox.pack_start(filechooserbutton,True,True,5)
        fchbox.pack_start(fccheckbox,False,False,5)
        mainvbox.pack_start(fchbox,False,False,5)
        buttonhbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        cancelbutton = Gtk.Button("Cancel")
        makebutton = Gtk.Button("Make Game")
        makebutton.connect("clicked",self.on_button_make_clicked, NameEntry, syscombobox, 
                           corecombobox, filechooserbutton, fccheckbox)
        buttonhbox.pack_end(makebutton,False,False,5)
        buttonhbox.pack_end(cancelbutton,False,False,5)
        cancelbutton.connect("clicked",self.Destroy_Window)
        mainvbox.pack_start(buttonhbox,False,False,5)
        
        
            
        self.add(mainvbox)
        self.connect("delete-event",self.On_Delete)
        
    def on_button_make_clicked(self,Button,NameEntry,syscombobox,corecombobox,
                                    filechooserbutton, CheckBox):
        domake = True
        gamename = NameEntry.get_text()
        if gamename != "":
            if not filechooserbutton.get_filenames():
                popup = ErrorPopupWindow("Choose File", "You must have a game file")
                popup.set_transient_for(self)
                popup.show_all()
                domake = False
            else:
                filename = filechooserbutton.get_filenames()[0]
                try:
                    active = syscombobox.get_active()
                    model = syscombobox.get_model()
                    siter = model.get_iter(active)
                    systext = model.get(siter,0)[0]
                    try:
                        active = corecombobox.get_active()
                        model = corecombobox.get_model()
                        siter = model.get_iter(active)
                        coretext = model.get(siter,0)[0]
                    except:
                        popup = ErrorPopupWindow("Choose Core", "You must choose a core")
                        popup.set_transient_for(self)
                        popup.show_all()
                        domake = False
                except:
                    popup = ErrorPopupWindow("Choose File", "You must choose a system")
                    popup.set_transient_for(self)
                    popup.show_all()
                    domake = False
                if domake:
                    gamedir = Globals.DataDir+"Games/"+systext+"/"+gamename
                    if os.path.isdir(gamedir):
                        popup = ErrorPopupWindow("Game already exists", "A game of that name already exists, remove it first")
                        popup.set_transient_for(self)
                        popup.show_all()
                        domake = False
        else:
            popup = ErrorPopupWindow("Game Name Empty", "Your game name cannot be empty")
            popup.set_transient_for(self)
            popup.show_all()
            domake = False
        if domake:
            os.makedirs(gamedir)
            #print gamename
            #print systext
            #print coretext
            gamefilename = filename.split("/")[-1]
            gameelem = ET.Element("Game",attrib={"name":gamename,
                                                 "core":coretext,
                                                 "filename":gamefilename,
                                                 "system":systext})
            found = False
            for system in Globals.GamesXML.findall("System"):
                if system.get("name") == systext:
                    found = True
                    system.append(ET.Element("Game",attrib={"name":gamename,
                                                            "core":coretext}))
            if not found:
                system = ET.Element("System",attrib={"name",systext})
                system.append(ET.Element("Game",attrib={"name":gamename,
                                                            "core":coretext}))
                Globals.GamesXML.append(system)
            Globals.Update_Games()
            with open(Globals.DataDir+"Systems/System_"+systext+"/system.xml",'r') as sysfile:
                sysxml = ET.XML(sysfile.read())
            syscontrols = sysxml.find("Controls")
            syscontrols.set("inherit","True")
            gameelem.append(syscontrols)
            with open(gamedir+"/game.xml",'w') as gamefile:
                gamefile.write(ET.tostring(gameelem))
            shutil.copy(filename, gamedir+"/"+gamefilename)
            os.makedirs(gamedir+"/savestates")
            os.makedirs(gamedir+"/patches")
            os.makedirs(gamedir+"/screenshots")
            self.Destroy_Window(self)
    
    def File_Selected(self,FileSelector,CheckBox):
        filename = FileSelector.get_filenames()[0].split("/")[-1]
        if (filename.endswith(".tar.gz") or
            filename.endswith(".tar.bz2") or
            filename.endswith(".tar") or
            filename.endswith(".zip")):
            
            CheckBox.set_sensitive(True)
        else:
            CheckBox.set_active(False)
            CheckBox.set_sensitive(False)
    
    def System_Box_Changed(self,SysComboBox,CoreComboBox):
        active = SysComboBox.get_active()
        model = SysComboBox.get_model()
        siter = model.get_iter(active)
        systext = model.get(siter,0)[0]
        CoreComboBox.set_sensitive(True)
        CoreComboBox.remove_all()
        CoreComboBox.append_text("(Default Core)")
        for i in Globals.Cores:
            if i.split("/")[0] == systext:
                CoreComboBox.append_text("".join(i.split("/")[1:]))
        pass
    
    def Destroy_Window(self,widget1):
        self.destroy()
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_MAKEGAME
        
    def On_Delete(self,Window,ResponseType):
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_MAKEGAME
        pass
        