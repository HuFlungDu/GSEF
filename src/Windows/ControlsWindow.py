from gi.repository import GtkClutter as cluttergtk #@UnresolvedImport   # must be the first to be imported
from gi.repository import Clutter as clutter #@UnresolvedImport
from gi.repository import Gtk, Gdk #@UnresolvedImport
from gi.repository import GObject as gobject #@UnresolvedImport
import sys
import Globals#@UnresolvedImport
from Popups import ConfirmationDialog
from Popups import ControlDialog
import shutil
import xml.etree.ElementTree as ET
import time

class ControlTree(Gtk.TreeView):
    def __init__(self,TreeStore=None):
        Gtk.TreeView.__init__(self,TreeStore)
        tvcolumn = Gtk.TreeViewColumn('Name')
        tvcolumn2 = Gtk.TreeViewColumn('Mapping')
        self.append_column(tvcolumn)
        self.append_column(tvcolumn2)
        cell = Gtk.CellRendererText()
        cell2 = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, False)
        tvcolumn2.pack_start(cell2, True)
        tvcolumn.set_cell_data_func(cell, self.get_xml_name)
        tvcolumn2.set_cell_data_func(cell2, self.get_xml_mapping)
    
    def get_xml_name(self, Column, Cell, Model, Iter, UserData):
        (element,) = Model.get(Iter,0)
        Cell.set_property('text', element.get("name"))
        
    def get_xml_mapping(self, Column, Cell, Model, Iter, UserData):
        (element,) = Model.get(Iter,0)
        Cell.set_property('text',element.get("Mapping"))

class ControlTreeStore(Gtk.TreeStore):
    def __init__(self,ControlData,Name):
        Gtk.TreeStore.__init__(self,gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT)
        self.sysname = Name
        self.generateTreeStore(ControlData)
    def generateTreeStore(self,XMLItem):
        for i in list(XMLItem):
            self.generateTreeStoreR(i)

    def generateTreeStoreR(self,XMLItem, parent=None):
        newparent=self.append(parent,[XMLItem,XMLItem])
        for i in list(XMLItem):
            self.generateTreeStoreR(i,newparent)

class ControlsWindow(Gtk.Window):
    def __init__(self):
        Globals.OpenWindows |= Globals.WINDOWTYPE_CONTROLS
        Gtk.Window.__init__(self,title="Manage games")
        
        self.set_default_size(500,500)
        notebook = Gtk.Notebook()
        
        controlsbox, xmls = self.Get_Controls_Box()
        audiobox = self.Get_Audio_Box()
        generalbox = self.Get_General_Box()
        self.connect("delete-event",self.On_Delete,xmls)
        notebook.append_page(controlsbox,Gtk.Label("Controls"))
        notebook.append_page(audiobox,Gtk.Label("Audio"))
        notebook.append_page(generalbox,Gtk.Label("General"))
        
        self.add(notebook)
        
    def Get_General_Box(self):
        def EnableRewindChecked(widget,rewindvbox):
            if widget.get_active():
                rewindvbox.set_sensitive(True)
                Globals.SettingsXML.find("Rewind").set("Enabled","True")
            else:
                rewindvbox.set_sensitive(False)
                Globals.SettingsXML.find("Rewind").set("Enabled","False")
                
        def EnableCompressionChecked(widget):
            if widget.get_active():
                Globals.SettingsXML.find("Rewind").set("Compress","True")
            else:
                Globals.SettingsXML.find("Rewind").set("Compress","False")
        def FrequencySpinnerChange(widget):
            Globals.SettingsXML.find("Rewind").set("Frames",str(widget.get_value_as_int()))
        def SizeSpinnerChange(widget):
            Globals.SettingsXML.find("Rewind").set("Size",str(widget.get_value_as_int()))
        
        rewind = Globals.SettingsXML.find("Rewind")
        enabled = rewind.get("Enabled") == "True"
        frames = int(rewind.get("Frames"))
        size = int(rewind.get("Size"))
        compression = rewind.get("Compress") == "True"
        mainvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        rewindvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        EnableRewindBox = Gtk.CheckButton.new_with_label("Enable rewind")
        RewindFramesLabel = Gtk.Label("Rewind state frequency (frames)")
        RewindFrequencySpin = Gtk.SpinButton.new_with_range(1,
                                                  60,
                                                  1)
        RewindFramesHBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        RewindFramesHBox.pack_start(RewindFramesLabel,True,True,5)
        RewindFramesHBox.pack_start(RewindFrequencySpin,False,False,5)
        
        RewindSizeLabel = Gtk.Label("Reserved space for rewind (mb)")
        RewindSizeSpin = Gtk.SpinButton.new_with_range(1,
                                                  36000,
                                                  1)
        RewindSizeHBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        RewindSizeHBox.pack_start(RewindSizeLabel,True,True,5)
        RewindSizeHBox.pack_start(RewindSizeSpin,False,False,5)
        
        EnableCompressionBox = Gtk.CheckButton.new_with_label("Enable compression (More CPU, less RAM)")
        EnableRewindBox.connect("toggled",EnableRewindChecked,rewindvbox)
        EnableCompressionBox.connect("toggled",EnableCompressionChecked)
        RewindFrequencySpin.connect("value-changed",FrequencySpinnerChange)
        RewindSizeSpin.connect("value-changed",SizeSpinnerChange)
        mainvbox.pack_start(EnableRewindBox,False,False,5)
        rewindvbox.pack_start(RewindFramesHBox,False,False,5)
        rewindvbox.pack_start(RewindSizeHBox,False,False,5)
        rewindvbox.pack_start(EnableCompressionBox,False,False,5)
        mainvbox.pack_start(rewindvbox,False,False,5)
        RewindFrequencySpin.set_value(frames)
        RewindSizeSpin.set_value(size)
        EnableRewindBox.set_active(enabled)
        EnableCompressionBox.set_active(compression)
        EnableRewindChecked(EnableRewindBox,rewindvbox)
        
        return mainvbox
        pass
        
    def Get_Audio_Box(self):
        def Update_Frequency_Values(widget,preedit,userdata,scale,entry):
            print widget == scale
            print widget, scale
            if widget == scale:
                entry.set_text(str(int(userdata)))
        maingrid = Gtk.Table(len(Globals.Systems),2,False)
        maingrid.attach(Gtk.Label("Input frequencies"),0,3,0,1,Gtk.AttachOptions.FILL,0)
        row = 1
        for sys in Globals.Systems:
            sysxmlpath = "{0}Systems/System_{1}/system.xml".format(Globals.DataDir,sys)
            with open(sysxmlpath,'r') as sysfile:
                sysxml = ET.XML(sysfile.read())
            frequencyrange = map(int,sysxml.find("Sound").get("FrequencyRange").split("-"))
            frequency = int(sysxml.find("Sound").get("Frequency"))
            label = Gtk.Label(sys)
            if frequencyrange[0] != frequencyrange[1]:
                scale = Gtk.HScale.new_with_range(frequencyrange[0],
                                                  frequencyrange[1],
                                                  1)
                scale.set_value(frequency)
                maingrid.attach(label,0,1,row,row+1,Gtk.AttachOptions.SHRINK,0)
                maingrid.attach(scale,1,2,row,row+1,Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL,0)
                entry = Gtk.Entry()
                entry.set_text(str(frequency))
                maingrid.attach(entry,2,3,row,row+1,Gtk.AttachOptions.FILL,0)
                entry.connect("preedit-changed",Update_Frequency_Values,
                              scale,entry)
                scale.connect("value-changed", lambda widget,scale,entry: Update_Frequency_Values(widget,widget.get_value(),widget.get_value(),scale,entry),
                              scale,entry)
                row += 1

        return maingrid
    
        
    def Get_Controls_Box(self):
        mainvbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        controltrees = []
        xmls = []
        syscombobox = Gtk.ComboBoxText()
        controltrees.append(ControlTreeStore(Globals.SettingsXML.find("Hotkeys"), "Hotkeys"))
        syscombobox.append_text("Hotkeys")
        for sys in Globals.Systems:
            sysxmlpath = "{0}Systems/System_{1}/system.xml".format(Globals.DataDir,sys)
            with open(sysxmlpath,'r') as sysfile:
                sysxml = ET.XML(sysfile.read())
            controltrees.append(ControlTreeStore(sysxml.find("Controls"), sysxml.get("name")))
            xmls.append(sysxml)
            syscombobox.append_text(sys)
        syscombobox.set_active(0)
        scrolledwindow = Gtk.ScrolledWindow()
        treeView = ControlTree()
        syscombobox.connect("changed",self.System_Box_Changed, controltrees, treeView)
        treeView.connect("row-activated", self.SetControl)
        self.System_Box_Changed(syscombobox,controltrees,treeView)
        scrolledwindow.add(treeView)
        mainvbox.pack_start(syscombobox,False,False,5)
        mainvbox.pack_start(scrolledwindow,True,True,5)
        return mainvbox,xmls
        
    def Destroy_Window(self,widget1):
        self.destroy()
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_CONTROLS
        
    def On_Delete(self,Window,ResponseType, xmls):
        for sys, xml in zip(Globals.Systems, xmls):
            sysxmlpath = "{0}Systems/System_{1}/system.xml".format(Globals.DataDir,sys)
            with open(sysxmlpath,'w') as sysfile: 
                sysfile.write(ET.tostring(xml))
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_CONTROLS
        
    def SetControl(self, TreeView, Path, Column):
        model = TreeView.get_model()
        iter = model.get_iter(Path)
        (mapping,) = model.get(iter,1)
        if mapping.get("Mapping") != None:
            (ControlXML,) = model.get(iter,0)
            dialog = ControlDialog(ControlXML)
            dialog.connect("response",self.Control_Dialog_Return)
            dialog.connect("key-press-event", self.ControlsKeyPress, mapping)
            dialog.connect("joypad-action-event", self.ButtonPress, mapping)
            dialog.set_transient_for(self)
            dialog.show_all()
            
    def ButtonPress(self,widget,event,mapping):
        joypad = event.Pad
        button = ["Axis","Button"][event.Button]
        buttonnum = event.Num
        value = event.Value
        if event.Button:
            cmd = "JP{}::{} {}".format(joypad,button,buttonnum)
        else:
            cmd = "JP{}::{} {} {}".format(joypad,button, buttonnum, "Positive" if value > 0 else "Negative")
        mapping.set("Mapping",cmd)
        widget.destroy()
        self.queue_draw()
    
    def ControlsKeyPress(self, widget, event, mapping):
        modkeys = ["Control_R", "Shift_R", "Alt_R", "Control_L", "Super_L", 
                   "Super_R", "Alt_L", "Shift_L", "Meta_L", "Meta_R"]
        masks = {'GDK_SHIFT_MASK':'Shift',
                 'GDK_CONTROL_MASK':'Control',
                 'GDK_SUPER_MASK':'Super',
                 'GDK_MOD1_MASK':'Alt'
                 }
        
        if not Gdk.keyval_name(event.get_keyval()[1]) in modkeys:
            modifiers = []
            for mod in event.get_state().value_names:
                try:
                    modifiers.append(masks[mod])
                except KeyError:
                    pass
            keystring = ""
            for mod in modifiers:
                keystring += mod + "+"
            try:
                keyname = chr(event.get_keyval()[1]).upper()
                if keyname == " ":
                    keyname = "Space"
            except ValueError:
                keyname = Gdk.keyval_name(Gdk.keyval_to_upper(event.get_keyval()[1]))
            keystring +=  keyname
            mapping.set("Mapping",keystring)
            widget.destroy()
            self.queue_draw()
    
    def Control_Dialog_Return(self, Window, ResponseType):
        pass
    
    def System_Box_Changed(self,SysComboBox,controltrees, treeView):
        active = SysComboBox.get_active()
        model = SysComboBox.get_model()
        siter = model.get_iter(active)
        (systext,) = model.get(siter,0)
        for sys in controltrees:
            if systext == sys.sysname:
                treeView.set_model(sys)
                break