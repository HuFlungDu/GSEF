#from gi.repository import GtkClutter as cluttergtk #@UnresolvedImport   # must be the first to be imported
from gi.repository import Gtk, Gdk
from gi.repository import GObject
#from pyglet.gl import *
from Widgets import GtkGlDrawingArea
from OpenGL.GL.shaders import *
from OpenGL.GL import *
#from gi.repository import Clutter as clutter #@UnresolvedImport
#from gi.repository import Cogl as cogl #@UnresolvedImport
import sys
import os
import Globals#@UnresolvedImport
import re
from CompressionWrapper import Archive#@UnresolvedImport
from Popups import ErrorPopupWindow
import xml.etree.ElementTree as ET
import SettingsCheck #@UnresolvedImport
from ManageSystemsWindow import ManageSystemsWindow#@UnresolvedImport
from MakeGameWindow import MakeGameWindow
from ManageGamesWindow import ManageGamesWindow
from ControlsWindow import ControlsWindow
import Callbacks
import numpy


def ReadFile(filename):
    readfile = open(filename,'r')
    source = readfile.read()
    readfile.close()
    return source
def ReadBinaryFile(filename):
    readfile = open(filename,'rb')
    source = readfile.read()
    readfile.close()
    return source

def MakeBuffer(target, data, size):
    TempBuffer = glGenBuffers(1)
    glBindBuffer(target, TempBuffer)
    glBufferData(target, size, data, GL_STATIC_DRAW)
    return TempBuffer



'''class GLContextWidget(Gtk.DrawingArea):
    __gtype_name__ = 'GLArea'

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        MainVertexData = numpy.array([-1,1,0,1,7,1,0,1,-1,-1,0,1,7,-1,0,1],numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
    def realize(self):
        window = self.get_window()

    def update_texture(self,texture,width = 0, height = 0, x_pot_waste = 0, y_pot_waste = 0):
        pass'''
"""class ClutterGLArea(clutter.Actor):
    __gtype_name__ = 'GLArea'

    def __init__(self):
        self.texture = None
        clutter.Actor.__init__(self)


    def update_texture(self,texture,textype,gl_target=None, width = 0, height = 0, x_pot_waste = 0, y_pot_waste = 0, pformat = cogl.PixelFormat.ANY):
        '''if textype == "cogl":
            self.texture = texture
        elif textype == "opengl":
            tex = clutter.Texture()
            ctex = tex.get_cogl_texture()
            print ctex
            self.texture = cogl.texture_new_from_foreign(texture,gl_target,width,height,x_pot_waste,y_pot_waste, pformat)
        self.queue_redraw()'''
        pass
    def do_paint(self):
        if self.texture != None:
            cogl.set_source_texture(self.texture)
            cogl.rectangle(0,0,self.get_width(),self.get_height())"""

class timed_label(Gtk.Label):

    def add_text_timer(self,text,timer):
        self.set_text(text)
        GObject.timeout_add(timer,self._timer_callback,text)

    def _timer_callback(self,text):
        if self.get_text() == text:
            self.set_text("")

class MainWindow(Gtk.Window):
    UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action="GameMenu">
        <menuitem action='Game_PlayGame' />
        <menuitem action='Game_MakeGame' />
        <menuitem action='Game_ManageGames' />
        <menuitem action='Game_Quit' />
    </menu>
    <menu action='SystemMenu'>
      <menuitem action='System_InstallSystem' />
      <menuitem action='System_InstallCore' />
      <menuitem action='System_ManageSystemsAndCores' />
    </menu>
    <menu action='SettingsMenu'>
      <menuitem action='Settings_Controls' />
      <menuitem action='Settings_Calibrate' />
      <menuitem action='Settings_AspectRatio' />
    </menu>
  </menubar>
</ui>
"""

    def __init__(self):
        Globals.OpenWindows |= Globals.WINDOWTYPE_MAINWINDOW
        Gtk.Window.__init__(self, title="GSEF")

        #self.set_default_size(width, height)

        action_group = Gtk.ActionGroup("my_actions")

        self.add_menu_actions(action_group)
        #self.add_edit_menu_actions(action_group)
        #self.add_choices_menu_actions(action_group)

        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)

        box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.FPSlabel = Gtk.Label("")
        self.statusLabel = timed_label("No Game Loaded")
        box2.pack_start(self.FPSlabel,True,False,0)
        box2.pack_start(self.statusLabel,True,False,0)

        #self.clutterembed = cluttergtk.Embed()
        #self.vbox.pack_start(self.clutterembed,True,True,0)
        #self.clutterembed.realize()
        #self.clutterstage = self.clutterembed.get_stage()
        self.glArea = GtkGlDrawingArea()
        #color = clutter.Color()
        #self.clutterstage.set_color(color)
        box.pack_start(self.glArea, True, True, 0)
        box.pack_start(box2, False, True, 0)
        #self.glArea = ClutterGLArea()
        #self.clutterstage.add_actor(self.glArea)
        Callbacks.UpdatePicture = self.glArea.update_texture
        #label = Gtk.Label("Right-click to see the popup menu.")
        #eventbox.add(label)

        self.popup = uimanager.get_widget("/PopupMenu")

        self.connect("key-press-event", self.KeyPressed)
        self.connect("key-release-event", self.KeyReleased)

        self.add(box)

    def KeyPressed(self, widget, event):
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
            self.setControl(keystring, Globals.Controls, 1)
            self.setControl(keystring, Globals.Hotkeys, 1)
            Globals.system.update_controls(Globals.Controls)
    def KeyReleased(self,widget,event):
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
            self.clearControl(keystring, Globals.Controls)
            self.clearControl(keystring, Globals.Hotkeys)
            Globals.system.update_controls(Globals.Controls)

    def clearControl(self, control, dic):
        for i in dic:
            try:
                if dic[i].get_mapping() == control.split("+")[-1]:
                    dic[i].set_state(0)

            except AttributeError:
                self.clearControl(control, dic[i])

    def setControl(self, control, dic, value):
        for i in dic:
            try:
                if dic[i].get_mapping() == control:
                    if dic[i].get_digital():
                        dic[i].set_state(1 if dic[i].get_state() else 2)
                    else:
                        dic[i].set_state(dic[i].get_sensitivity()*value)

            except AttributeError:
                self.setControl(control, dic[i],value)

    def add_menu_actions(self, action_group):
        action_game_menu = Gtk.Action("GameMenu", "Game", None, None)
        action_group.add_action(action_game_menu)
        action_system_menu = Gtk.Action("SystemMenu", "System", None, None)
        action_group.add_action(action_system_menu)
        action_settings_menu = Gtk.Action("SettingsMenu", "Settings", None, None)
        action_group.add_action(action_settings_menu)

        action_InstallSystem = Gtk.Action("System_InstallSystem", "Install System",
                                          "Install a new System", None)
        action_InstallSystem.connect("activate", self.on_menu_install_system)
        action_group.add_action_with_accel(action_InstallSystem, None)

        action_InstallCore = Gtk.Action("System_InstallCore", "Install Core",
                                        "Install a new Core", None)
        action_InstallCore.connect("activate", self.on_menu_install_core)
        action_group.add_action(action_InstallCore)

        action_ManageSystems = Gtk.Action("System_ManageSystemsAndCores", "Manage Systems and Cores",
                                        "Manage Systems and Cores", None)
        action_ManageSystems.connect("activate", self.on_menu_manage_systems_and_cores)
        action_group.add_action(action_ManageSystems)

        action_PlayGame = Gtk.Action("Game_PlayGame", "Play Game", None, None)
        #action_Quit.connect("activate", self.on_menu_quit)
        action_group.add_action(action_PlayGame)

        action_MakeGame = Gtk.Action("Game_MakeGame", "Make Game", None, None)
        action_MakeGame.connect("activate", self.on_menu_make_game)
        action_group.add_action(action_MakeGame)

        action_ManageGames = Gtk.Action("Game_ManageGames", "Manage Games", None, None)
        action_ManageGames.connect("activate", self.on_menu_manage_games)
        action_group.add_action(action_ManageGames)

        action_Controls = Gtk.Action("Settings_Controls", "Controls", None, None)
        action_Controls.connect("activate", self.on_menu_controls)
        action_group.add_action(action_Controls)

        action_Controls = Gtk.Action("Settings_Calibrate", "Calibrate joysticks", None, None)
        action_Controls.connect("activate", self.on_menu_calibrate)
        action_group.add_action(action_Controls)

        action_AspectRatio = Gtk.ToggleAction("Settings_AspectRatio", "Keep Correct Aspect Ratio", None, None)
        if Globals.SettingsXML.find("AspectRatio").get("keep") == "True":
            action_AspectRatio.set_active(True)
        action_AspectRatio.connect("activate", self.on_menu_aspectratio)
        action_group.add_action(action_AspectRatio)

        action_Quit = Gtk.Action("Game_Quit", "Quit", None, None)
        action_Quit.connect("activate", self.on_menu_quit)
        action_group.add_action(action_Quit)


    def create_ui_manager(self):
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(self.UI_INFO)

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def on_menu_aspectratio(self, widget):
        if Globals.SettingsXML.find("AspectRatio").get("keep") == "True":
            Globals.SettingsXML.find("AspectRatio").set("keep","False")
        else:
            Globals.SettingsXML.find("AspectRatio").set("keep","True")

    def on_menu_install_system(self, widget):
        if not Globals.OpenWindows & Globals.WINDOWTYPE_FILECHOOSER:
            filter = Gtk.FileFilter()
            filter.add_pattern("*.zip")
            filter.add_pattern("*.tar")
            filter.add_pattern("*.tar.gz")
            filter.add_pattern("*.tar.bz2")
            filter.set_name("Compressed System Files")
            path = Globals.SettingsXML.find("Paths").find("LastAccessedSystem").get("path")
            filechooser = Gtk.FileChooserDialog(title="Select System",
                                                buttons= (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
            filechooser.set_transient_for(self)
            filechooser.connect("response",self.System_Install_Response)
            filechooser.add_filter(filter)
            filechooser.show_all()
            Globals.OpenWindows |= Globals.WINDOWTYPE_FILECHOOSER

    def System_Install_Response(self,FileChooser,Response):
        SystemSettingsTree = {("",1,("name",),SettingsCheck.SystemNameSanityCheck) :None}
        if Response == Gtk.ResponseType.ACCEPT:
            filename = FileChooser.get_filename()
            SystemArchive = Archive(filename,'r')
            try:
                settingsstring = SystemArchive.read("system.xml")
                SystemXML = ET.XML(settingsstring)
                ValidSettings = SettingsCheck.check_settings(SystemSettingsTree, SystemXML)
                if not ValidSettings:
                    raise Exception
                systemname = SystemXML.get("name")
                if not os.path.isdir(Globals.DataDir+"Systems/System_"+systemname):
                    os.mkdir(Globals.DataDir+"Systems/System_"+systemname)
                    if not os.path.isdir(Globals.DataDir+"Games/"+systemname):
                        os.mkdir(Globals.DataDir+"Games/"+systemname)
                    SystemArchive.extractall(path=Globals.DataDir+"Systems/System_"+systemname)
                    Globals.Systems.append(systemname)
                    popup = ErrorPopupWindow("System Installed","System installed successfully!")
                    popup.set_transient_for(self)
                    popup.show_all()
                else:
                    popup = ErrorPopupWindow("System already exists","System already exists, uninstall the system first.")
                    popup.set_transient_for(self)
                    popup.show_all()
            except:
                popup = ErrorPopupWindow("Malformed System","Archive containing the system is malformed, try redownloading the archive")
                popup.set_transient_for(self)
                popup.show_all()
        FileChooser.destroy()
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_FILECHOOSER

    def on_menu_install_core(self, widget):
        if not Globals.OpenWindows & Globals.WINDOWTYPE_FILECHOOSER:
            filter = Gtk.FileFilter()
            filter.add_pattern("*.zip")
            filter.add_pattern("*.tar")
            filter.add_pattern("*.tar.gz")
            filter.add_pattern("*.tar.bz2")
            filter.set_name("Compressed System Files")
            path = Globals.SettingsXML.find("Paths").find("LastAccessedCore").get("path")
            filechooser = Gtk.FileChooserDialog(title="Select System",
                                                buttons= (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
            filechooser.set_transient_for(self)
            filechooser.connect("response",self.Core_Install_Response)
            filechooser.add_filter(filter)
            filechooser.show_all()
            Globals.OpenWindows |= Globals.WINDOWTYPE_FILECHOOSER

    def Core_Install_Response(self,FileChooser,Response):
        CoreSettingsTree = {("",1,("name","system"),SettingsCheck.CoreNameSanityCheck) : None}
        if Response == Gtk.ResponseType.ACCEPT:
            filename = FileChooser.get_filename()
            SystemArchive = Archive(filename,'r')
            try:
                settingsstring = SystemArchive.read("core.xml")
                CoreXML = ET.XML(settingsstring)
                ValidSettings = SettingsCheck.check_settings(CoreSettingsTree, CoreXML)
                if not ValidSettings:
                    raise Exception("Invalid Core Settings")
                systemname = CoreXML.get("system")
                corename = CoreXML.get("name")
                if os.path.isdir(Globals.DataDir+"Systems/System_"+systemname):
                    if not os.path.isdir(Globals.DataDir+"Systems/System_"+systemname+"/"+corename):
                        os.mkdir(Globals.DataDir+"Systems/System_"+systemname+"/Core_"+corename)
                        SystemArchive.extractall(path=Globals.DataDir+"Systems/System_"+systemname+"/Core_"+ corename)
                        Globals.Cores.append(systemname+"/"+corename)
                        popup = ErrorPopupWindow("Core Installed","Core installed successfully!")
                        popup.set_transient_for(self)
                        popup.show_all()
                    else:
                        popup = ErrorPopupWindow("Core already exists","Core already exists, uninstall the core first.")
                        popup.set_transient_for(self)
                        popup.show_all()
                else:
                    popup = ErrorPopupWindow("System not found","System: " + systemname + " not found, please install the system before the core")
                    popup.set_transient_for(self)
                    popup.show_all()
            except Exception as e:
                print e
                popup = ErrorPopupWindow("Malformed Core","Archive containing the core is malformed, try redownloading the archive")
                popup.set_transient_for(self)
                popup.show_all()
        FileChooser.destroy()
        Globals.OpenWindows &= ~Globals.WINDOWTYPE_FILECHOOSER

    def on_menu_manage_systems_and_cores(self, widget):
        if not Globals.OpenWindows & Globals.WINDOWTYPE_MANAGESYSTEMS:
            ManagerWindow = ManageSystemsWindow()
            ManagerWindow.set_transient_for(self)
            ManagerWindow.show_all()

    def on_menu_make_game(self,widget):
        if not len(Globals.Systems) or not len(Globals.Cores):
            popup = ErrorPopupWindow("No Systems or Core", "A game cannot be created without at least one system and one core")
            popup.set_transient_for(self)
            popup.show_all()
        elif not Globals.OpenWindows & Globals.WINDOWTYPE_MAKEGAME:
            GameMakerWindow = MakeGameWindow()
            GameMakerWindow.set_transient_for(self)
            GameMakerWindow.show_all()

    def on_menu_manage_games(self, widget):
        print "manage games"
        if not Globals.OpenWindows & Globals.WINDOWTYPE_MANAGEGAMES:
            ManagerWindow = ManageGamesWindow()
            ManagerWindow.set_transient_for(self)
            ManagerWindow.show_all()

    def on_menu_controls(self,widget):
        if not Globals.OpenWindows & Globals.WINDOWTYPE_CONTROLS:
            controlsWindow = ControlsWindow()
            controlsWindow.set_transient_for(self)
            controlsWindow.show_all()

    def on_menu_calibrate(self,widget):
        return
        if not Globals.OpenWindows & Globals.WINDOWTYPE_CONTROLS:
            controlsWindow = ControlsWindow()
            controlsWindow.set_transient_for(self)
            controlsWindow.show_all()

    def on_menu_quit(self, widget):
        self.destroy()


    def on_button_press_event(self, widget, event):
        # Check if right mouse button was preseed
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popup.popup(None, None, None, None, event.button, event.time)
            return True # event has been handled
