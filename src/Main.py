from gi.repository import GtkClutter as cluttergtk #@UnresolvedImport   # must be the first to be imported
from gi.repository import Gtk, Gdk #@UnresolvedImport
from gi.repository import GObject
import Globals
import sys
import os
import xml.etree.ElementTree as ET
from OpenGL.GL import *

import multiprocessing

from Windows import MainWindow#@UnresolvedImport
from Windows import ErrorPopupWindow#@UnresolvedImport
cluttergtk.init(sys.argv)
import SettingsCheck
from functools import partial
import Callbacks
import struct

import xordiff

import pygame
pygame.init()
import pyaudio
PyAudio = pyaudio.PyAudio()
import numpy
from pymouse import PyMouse

import datetime
import time

DefaultSettings = '''<Settings>
    <Paths>
        <LastAccessedSystem path="~" />
        <LastAccessedCore path="~" />
    </Paths>
    <AspectRatio keep="True" />
    <Window height="200" width="200" />
    <Hotkeys>
        <Button Mapping="None" name="Save State" />
        <Button Mapping="None" name="Load State" />
        <Button Mapping="None" name="Increment State Slot" />
        <Button Mapping="None" name="Decrement State Slot" />
        <Button Mapping="None" name="Rewind" />
        <Button Mapping="None" name="Pause" />
        <Button Mapping="None" name="Turbo" />
        <Button Mapping="None" name="Hard Reset" />
        <Button Mapping="None" name="Soft Reset" />
    </Hotkeys>
    <Rewind Frames="1" Size="1" Enabled="True" />
</Settings>'''
    
#Main class for the project

class System(object):
    def __init__(self,name):
        self.rewinding = False
        self.name = name
        self.core = None
        self._gamepath = None
        sys.path.append(Globals.DataDir+"Systems/"+ "System_" + self.name)
        sys.path.append(Globals.DataDir+"Systems")
        system = __import__("System_"+name)
        self.system = system.system()
        sys.path.remove(Globals.DataDir+"Systems")
        #Get sound stuff from XML
        sysxmlpath = "{}Systems/System_{}/system.xml".format(Globals.DataDir, self.name)
        with open(sysxmlpath,'r') as xmlfile:
            self.xml = ET.XML(xmlfile.read())
        soundxml = self.xml.find("Sound")
        self.channels = int(soundxml.get("Channels"))
        bitlength = int(soundxml.get("Bitlength"))
        rate = int(soundxml.get("Frequency"))
        endianness = soundxml.get("Endianness")
        self.packing = "{}{}{}".format({"little":"<","big":">"}[endianness],self.channels,
                    {8:"B",16:"H",32:"I"}[bitlength])
        self.soundbuf_size = int(soundxml.get("BufferLength"))
        self.soundbuf_raw = ''
        self.soundbuf_buf = None
        self.running = True
        self.stream = PyAudio.open(format=pyaudio.paInt16,
                                   channels=2,
                                   rate = rate,
                                   output = True,
                                   frames_per_buffer = self.soundbuf_size)
        #pygame.mixer.quit()
        #pygame.mixer.init(frequency=rate, size=bitlength, channels=channels, buffer=self.soundbuf_size)
        #self.soundbuf = pygame.sndarray.make_sound(numpy.zeros( (self.soundbuf_size,2), dtype='uint16', order='C' ))
        #self.soundbuf_buf = self.soundbuf.get_buffer()
        Callbacks.UpdateAudio = self.update_audio
        Callbacks.PollInput = self.poll_input
    def load_core(self,corename):
        if self.core != corename:
            self.system.unload_core()
            self.system.load_core(corename)
            self.core = corename
    def load_game(self,gamepath, patchpath, patcher):
        self._gamepath = gamepath
        with open("{0}game.xml".format(gamepath),"r") as gamefile:
            gamexml = ET.XML(gamefile.read())
        gamefile = gamexml.get("filename")
        self.system.load_game(gamepath, gamefile, patchpath, patcher)
    def unload_core(self):
        self.system.unload_core()
        
    def serialize(self):
        return self.system.get_save_state_data()
    
    def unserialize(self,data):
        self.system.load_state(data)
    
    def save_state(self, statename):
        savedata = self.system.get_save_state_data()
        with open("{}savestates/{}".format(self._gamepath,statename),'w') as savefile:
            savefile.write(savedata)
            
    def load_state(self,statename):
        with open("{}savestates/{}".format(self._gamepath,statename),'r') as savefile:
            savedata = savefile.read()
        self.system.load_state(savedata)
        
    def toggle_pause(self):
        if self.running:
            self.running = False
            self.stream.stop_stream()
        else:
            self.running = True
            self.stream.start_stream()
    
    def toggle_power(self):
        pass
    
    def setControl(self,control, dic, value):
        for i in dic:
            try:
                if dic[i].get_mapping() == control:
                    if dic[i].get_digital():
                        dic[i].set_state(1)
                    else:
                        dic[i].set_state(round(dic[i].get_sensitivity()*value))
                    
            except AttributeError:
                self.setControl(control, dic[i],value)
    def clearControl(self,control, dic):
        for i in dic:
            try:
                if dic[i].get_mapping() == control.split("+")[-1]:
                    dic[i].set_state(0)
                    
            except AttributeError:
                self.clearControl(control, dic[i])
    
    def poll_input(self):
        if Globals.JoystickStates:
            for i, (joystick, oldjoystick) in enumerate(zip(Globals.JoystickStates,Globals.OldJoystickStates)):
                for j, (button, oldbutton) in enumerate(zip(joystick["Buttons"],oldjoystick["Buttons"])):
                    if button != oldbutton:
                        cmd = "JP{}::Button {}".format(i,j)
                        if button != 0:
                            self.setControl(cmd,Globals.Controls,button)
                            self.setControl(cmd,Globals.Hotkeys,button)
                        else:
                            self.clearControl(cmd,Globals.Controls)
                            self.clearControl(cmd,Globals.Hotkeys)
                for j, (axis, oldaxis) in enumerate(zip(joystick["Axes"],oldjoystick["Axes"])):
                    if axis != oldaxis:
                        cmd = "JP{}::Axis {} {}".format(i, j, "Positive" if axis > 0 else "Negative")
                        if axis != 0:
                            self.setControl(cmd,Globals.Controls,abs(axis))
                            self.setControl(cmd,Globals.Hotkeys,abs(axis))
                        else:
                            self.clearControl(cmd,Globals.Controls)
                            self.clearControl(cmd.replace("Negative","Positive"),Globals.Controls)
                            self.clearControl(cmd,Globals.Hotkeys)
                            self.clearControl(cmd.replace("Negative","Positive"),Globals.Hotkeys)
            Globals.system.update_controls(Globals.Controls)
         
        if self.CheckForMapping("Mouse-X", Globals.Controls) or self.CheckForMapping("Mouse-Y",Globals.Controls):
    
            MiddleX = Globals.Mainwindow.glArea.get_window().get_origin()[0] + \
                     Globals.Mainwindow.glArea.get_allocated_width()/2
            MiddleY = Globals.Mainwindow.glArea.get_window().get_origin()[1] + \
                     Globals.Mainwindow.glArea.get_allocated_height()/2
            MouseX = Globals.Mouse.position()[0] - MiddleX         
            MouseY = Globals.Mouse.position()[1] - MiddleY
            
            Globals.Mouse.move(MiddleX,MiddleY)
    
    def CheckForMapping(self, control, dic):
        for i in dic:
            try:
                if dic[i].get_mapping() == control:
                    return True
                    
            except AttributeError:
                return self.CheckForMapping(control, dic[i])
        
    def update_audio(self,samples):
        if self.rewinding:
            start = len(samples)
            stop = 0
            step = -self.channels
            slicestart = -self.channels
            sliceend = 0
        else:
            start = 0
            stop = len(samples)
            step = self.channels
            slicestart = 0
            sliceend = self.channels
        for i in xrange(start,stop,step):
            channels = samples[i+slicestart:i+sliceend]
            if len(channels):
                self.soundbuf_raw += struct.pack(self.packing, *channels)
            
            if len(self.soundbuf_raw) >= 256:
                self.stream.write(self.soundbuf_raw)
                self.soundbuf_raw = ''  
        return
        
    def update_controls(self,controldic):
        self.system.update_controls(controldic)
    
    def run_frame(self):
        self.system.run_frame()
        return True
        #GObject.timeout_add( 10, self.run_frame)
        
    def get_framerate(self):
        if self.system.check_core():
            return self.system.get_framerate()
        else:
            return -1
    
    def close(self):
        try:
            self.system.save_data()
        except:
            pass
        self.system.close()
        sys.path.remove(Globals.DataDir+"Systems/"+ "System_" + self.name)
        

class GSEF(object):
    def __init__(self):
        #Create data directories. Included in windows even though 
        #the project won't work in windows yet
        self.frames= 0
        self.oldtime = 0
        SettingsXML = self.Get_Settings()
        Globals.SettingsXML = SettingsXML
        self.window = MainWindow()
        self.ErrorMsg = None
        self.system = None
        self.rewinding = False
        Globals.load_game = partial(self.load_game,self)
        Globals.load_game = self.load_game
        Globals.Mainwindow = self.window
        Globals.Mouse = PyMouse()
        Globals.Joysticks = [pygame.joystick.Joystick(i) for i in xrange(pygame.joystick.get_count())]
        [i.init() for i in Globals.Joysticks]
        
        if not os.path.isdir(Globals.DataDir+"temp"):
            os.mkdir(Globals.DataDir+"temp")
        if not os.path.isdir(Globals.DataDir+"Systems"):
            os.mkdir(Globals.DataDir+"Systems")
        if not os.path.isdir(Globals.DataDir+"Games"):
            os.mkdir(Globals.DataDir+"Games")
        SystemSettingsTree = {("",1,("name",), SettingsCheck.SystemExistSanityCheck): None}
        CoreSettingsTree = {("",1,("name","system"),SettingsCheck.CoreNameSanityCheck) : None}
        
        for i in os.listdir(Globals.DataDir+"Systems"):
            if os.path.isdir(Globals.DataDir+"Systems/"+i):
                try:
                    with open(Globals.DataDir+"Systems/"+i+"/system.xml",'r') as settingsfile:
                        SystemXML = ET.XML(settingsfile.read())
                    if SettingsCheck.check_settings(SystemSettingsTree, SystemXML):
                        Globals.Systems.append((i)[7:])
                        for j in os.listdir(Globals.DataDir+"Systems/"+i):
                            if os.path.isdir(Globals.DataDir+"Systems/"+i+"/"+j):
                                try:
                                    settingsfile = open(Globals.DataDir+"Systems/"+i+"/" + j + "/core.xml",'r')
                                    with open(Globals.DataDir+"Systems/"+i+"/" + j + "/core.xml",'r') as settingsfile:
                                        CoreXML = ET.XML(settingsfile.read())
                                    if SettingsCheck.check_settings(CoreSettingsTree, CoreXML):
                                        Globals.Cores.append(i[7:]+"/"+j[5:])                                    
                                except:
                                    pass
                except:
                    pass
        
        self.systemrunning=False
        
        GamesXML = self.Get_Games()
               
        
        Globals.GamesXML = GamesXML
        
        Globals.Update_Games()
        Globals.WindowHeight = int(Globals.SettingsXML.find("Window").get("height"))
        Globals.WindowWidth = int(Globals.SettingsXML.find("Window").get("width"))        
        self.window.set_default_size(Globals.WindowWidth, Globals.WindowHeight)
        self.window.connect('check-resize', self.Window_Size_Changed)
        self.window.connect("delete-event", self.on_kill)
        self.window.connect("destroy", self.on_kill)
        self.window.show_all()
        
        self.framequeue = multiprocessing.Queue()
        childpipe ,self.loopingpipe = multiprocessing.Pipe()
        frameprocess = multiprocessing.Process(target = self.Frame_Thread,args=(self.framequeue,childpipe))
        frameprocess.start()
        Globals.Hotkeys = self.generateControls(Globals.SettingsXML.find("Hotkeys"))
        GObject.timeout_add(16,self.on_idle)
        
    def on_kill(self, *args):
        if Globals.system:
            Globals.system.close()
            Globals.system = None
        Gtk.main_quit()
        
    def on_idle(self):
        
        if Globals.system and Globals.Hotkeys["Rewind"].get_state() and len(Globals.StateSizes):
            Globals.system.rewinding = True
            
            Globals.system.unserialize(Globals.StateData[0])
            if len(Globals.StateData) > 1:
                if isinstance(Globals.StateData[1], xordiff.numpyxor):
                    Globals.StateData[1] = Globals.StateData[1].undiff(Globals.StateData[0])
                    Globals.StateSizes[1] = Globals.StateData[1]
            del(Globals.StateData[0])
            del(Globals.StateSizes[0])
        elif Globals.system:
            Globals.system.rewinding = False 
        rewind = Globals.SettingsXML.find("Rewind")
        if rewind.get("Enabled") == "True" and Globals.system and not Globals.system.rewinding:
            frames = int(rewind.get("Frames"))
            size = int(rewind.get("Size"))
            if not self.frames % frames:
                statedata = Globals.system.serialize()
                datalen = statedata.nbytes
                if len(Globals.StateData) and rewind.get("Compress") == "True":
                    Globals.StateData[0] = xordiff.numpyxor(Globals.StateData[0], statedata)
                    Globals.StateSizes[0] = Globals.StateData[0].nbytes
                Globals.StateData.insert(0,statedata)
                Globals.StateSizes.insert(0,datalen)
                while sum(Globals.StateSizes) > size*1048576:
                    Globals.StateData.pop()
                    Globals.StateSizes.pop()
            
            
        pygame.event.pump()
        Globals.OldJoystickStates = Globals.JoystickStates
        Globals.JoystickStates = []
        for joystick in Globals.Joysticks:
            Buttons = []
            Axes = []
            for i in range(0, joystick.get_numaxes()):
                Axes.append(joystick.get_axis(i))
            for i in range(0, joystick.get_numbuttons()):
                Buttons.append(joystick.get_button(i))
            Globals.JoystickStates.append({"Buttons":Buttons,"Axes":Axes})
            
            
        frames = 0
        if Globals.system and Globals.system.running:
            if not self.framequeue.empty():
                self.framequeue.get()
                frames += 1
    
            if frames:
                Globals.system.run_frame()
                self.frames += 1
                if int(time.time()) != self.oldtime:
                    self.framerate = self.frames
                    self.frames = 0
                    self.window.FPSlabel.set_text("FPS: {}".format(self.framerate))
                self.oldtime = int(time.time())

        return True
            
            
    
    def Frame_Thread(self, framequeue, pipe):
        variables = ["framerate", "running", "framestart"]
        framerate = 0
        running = False
        framestart = datetime.datetime.now()
        while (True):
            if pipe.poll():
                #Commands come in a tuple, first comes the command as a string
                #After that is the arguments required by that command
                command = pipe.recv()
                cmdstring = command[0]
                if cmdstring == "set":
                    variable = command[1]
                    value = command[2]
                    if variable in variables:
                        exec("{}=value".format(variable))
                elif cmdstring == "kill":
                    break
            if running:
                if framerate > 0:
                    difference = datetime.datetime.now()-framestart
                    while difference.microseconds/1000 >= 1000/framerate:
                        framestart += datetime.timedelta(milliseconds=1000/framerate)
                        difference = datetime.datetime.now()-framestart
                        framequeue.put("Run")
            if framerate:
                time.sleep(((1000/framerate)/2)/100.0)
            else:
                time.sleep(1)  
        
    
    def Get_Games(self):
        ValidGames = False
        GamesXML = None
        try:
            with open(Globals.DataDir+"Games/Games.xml", "r") as GamesFile:
                GamesText = GamesFile.read()
            ValidGames = True
        except IOError:
            pass
        
        #Description to follow through the settings tree for testing sanity
        GamesTree = {("System",0,("name",),SettingsCheck.SystemExistSanityCheck) : 
                        {("Game",0,("name",),SettingsCheck.GameNameSanityCheck): 
                            {("Patch",0,("name",),SettingsCheck.PatchNameSanityCheck):None}
                        }
                    }
        GameTree = {("",1,("name","core","filename","system"),SettingsCheck.GameSettingsSanityCheck) :
                        {("Controls",1,("inherit",),None): None                            
                        }
                    }
        PatchSanityLam = lambda game,name,format,filename,system: os.path.isfile(Globals.DataDir+"Games/"+system+"/"+game+"/patches/"+name+"/"+filename)
        PatchTree = {("",1,("game","name","format","filename","system"),PatchSanityLam) :
                        {("Controls",1,("inherit",),None): None                            
                        }
                    }
        
        #Make sure the settings file is valid XML
        if ValidGames:
            try:
                GamesXML = ET.XML(GamesText)
            except ET.ParseError:
                ValidGames = False
        
        #Validate the the settings use sane values
        if ValidGames:
            ValidGames = SettingsCheck.check_settings(GamesTree,GamesXML)
            
        #If the games XML file isn't sane, repopulate it manually
        if not ValidGames:
            popup = ErrorPopupWindow("Games not found","Game definitions not found, repopulating manually")
            popup.set_transient_for(self.window)
            popup.show_all()
            systemlam = lambda x: os.path.isdir(Globals.DataDir+"Games/"+x) and os.path.isdir(Globals.DataDir+"Systems/System_"+x)
            gamelam = lambda x: os.path.isdir(Globals.DataDir+"Games/"+system+"/"+x)
            patchlam = lambda x: os.path.isdir(Globals.DataDir+"Games/"+system+"/"+game+"/"+x)
            GamesXML = ET.XML("<Games/>")
            for system in filter(systemlam, os.listdir(Globals.DataDir+"Games")):
                SystemXML = ET.XML("<System/>")
                SystemXML.set("name",system)
                for game in filter(gamelam,os.listdir(Globals.DataDir+"Games/"+system)):
                    try:
                        with open(Globals.DataDir+"Games/"+system+"/"+game+"/game.xml",'r') as GameSettingsFile:
                            GameSettingsText = GameSettingsFile.read()
                        GameSettingsXML = ET.XML(GameSettingsText)
                        GameSane = SettingsCheck.check_settings(GameTree, GameSettingsXML)
                        if GameSane:
                            GameXML = ET.XML("<Game/>")
                            GameXML.set("name",game)
                            GameXML.set("core",GameSettingsXML.get("core"))
                            for patch in filter(patchlam,os.listdir(Globals.DataDir+"Games/"+system+"/"+game+"/patches")):
                                try:
                                    with open(Globals.DataDir+"Games/"+system+"/"+game+"/patches/"+patch+"/patch.xml",'r') as PatchSettingsFile:
                                        PatchSettingsText = PatchSettingsFile.read()
                                    PatchSettingsXML = ET.XML(PatchSettingsText)
                                    PatchSane = SettingsCheck.check_settings(PatchTree, PatchSettingsXML)
                                    if PatchSane:
                                        PatchXML = ET.XML("<Patch/>")
                                        PatchXML.set("name",patch)
                                        PatchXML.set("format",PatchSettingsXML.get("format"))
                                        GameXML.append(PatchXML)
                                except:
                                    pass
                            SystemXML.append(GameXML)
                    except:
                        pass
                GamesXML.append(SystemXML)        
        return GamesXML
        
    
    def Get_Settings(self):
        ValidSettings = False
        SettingsXML = None
        try:
            with open(Globals.DataDir+"Settings.xml", "r") as SettingsFile:
                SettingsText = SettingsFile.read()
            ValidSettings = True
        except IOError:
            pass
        
        #Description to follow through the settings tree for testing sanity
        SettingsTree = {("Paths",1,(),None) : 
                            {("LastAccessedSystem",1,("path",),SettingsCheck.DirectoryPathSanityCheck):None,
                             ("LastAccessedCore",1,("path",),SettingsCheck.DirectoryPathSanityCheck):None
                            },
                        ("Window",1,("width","height"),SettingsCheck.WindowSizeSanityCheck) :None,
                        ("AspectRatio",1,("keep",), lambda x: x == "True" or x == "False") : None,
                        ("Hotkeys",1,(),None) : {("Button",9,("Mapping","name"),None) : None},
                        ("Rewind",1,("Frames","Size","Enabled","Compress"), lambda f, s, e, c: f.isdigit() and s.isdigit() and (e == "False" or e == "True") and (c == "False" or c == "True")) : None
                        }
        
        SettingsXML = ET.XML(SettingsText)
        #Make sure the settings file is valid XML
        if ValidSettings:
            try:
                SettingsXML = ET.XML(SettingsText)
            except ET.ParseError:
                ValidSettings = False
        
        #Validate the the settings use sane values
        if ValidSettings:
            ValidSettings = SettingsCheck.check_settings(SettingsTree,SettingsXML)
        
        #If the settings aren't sane, replace them with the standard settings
        #May change later to only replace the parts that are not sane
        if not ValidSettings:
            try:
                SettingsXML = ET.XML(DefaultSettings)
                with open(Globals.DataDir+"Settings.xml", "w") as SettingsFile:
                    SettingsFile.write(DefaultSettings)
                popup = ErrorPopupWindow("Settings Not Found","Settings not found or corrupt, using default settings")
                popup.show_all()
            except:
                self.ErrorMsg = "Failed to write to settings file"
        return SettingsXML
         
    
    #When the window resizes, we need to change the preferred window size to that
    #That way when they come back, the window will be the same size
    def Window_Size_Changed(self,window):
        size = window.get_size()
        Globals.WindowHeight = size[1]
        Globals.WindowWidth = size[0]
        windowxml = Globals.SettingsXML.find("Window")
        windowxml.set("width",str(size[0]))
        windowxml.set("height",str(size[1]))
    
    
   
    
    def Run(self):
        Gtk.main()
        #Write out the changed settings, however they were changed
        with open(Globals.DataDir+"Settings.xml", "w") as SettingsFile:
            SettingsFile.write(ET.tostring(Globals.SettingsXML))
        with open(Globals.DataDir+"Games/Games.xml", "w") as GamesFile:
            GamesFile.write(ET.tostring(Globals.GamesXML))
        self.loopingpipe.send(("kill",))
    
    def load_game(self,systemname,corename,gamename,patchname):
        Globals.StateData = []
        Globals.StateSizes = []
        if Globals.system != None:
            Globals.system.close()
            Globals.system = System(systemname)
        else:
            Globals.system = System(systemname)
        Globals.system.load_core(corename)
        gamepath = "{0}Games/{1}/{2}/".format(Globals.DataDir,systemname,gamename)
        sysxmlpath = "{0}Systems/System_{1}/system.xml".format(Globals.DataDir,systemname)
        patchpath = "{0}{1}".format(gamepath,patchname)
        controlpath = "{0}game.xml".format(gamepath)
        with open(controlpath,'r') as controlxmlfile:
            controlxml = ET.XML(controlxmlfile.read())
        if controlxml.find("Controls").get("inherit") == "True":
            with open(sysxmlpath,'r') as controlxmlfile:
                controlxml = ET.XML(controlxmlfile.read())
        controlxml = controlxml.find("Controls")
        
        Globals.Hotkeys = self.generateControls(Globals.SettingsXML.find("Hotkeys"))
        Globals.Controls = self.generateControls(controlxml)
        
        patcher = None #Add patch stuff later
        Globals.system.update_controls(Globals.Controls)
        Globals.system.load_game(gamepath,patchpath,patcher)
        framerate = Globals.system.get_framerate()
        self.loopingpipe.send(("set","framerate",framerate))
        self.loopingpipe.send(("set","framestart",datetime.datetime.now()))
        self.loopingpipe.send(("set","running",True))
        self.window.statusLabel.add_text_timer("Loaded {}".format(gamename), 3000)
        
        #GObject.timeout_add( 1000/60, Globals.system.run_frame)
        
    def generateControls(self,XMLItem):
        def generateControlsR(XMLItem, parent=None):
            if XMLItem.get("Mapping"):
                digital = False
                if XMLItem.get("type") == "Digital":
                    digital = True
                return Control(XMLItem.get("Mapping"), XMLItem.tag, XMLItem.get("name"), digital)
    
            controls = {}
            for i in list(XMLItem):
                controls[i.get('name')] = generateControlsR(i)
            return controls
        controls = {}
        for i in list(XMLItem):
            controls[i.get("name")] = generateControlsR(i)
        return controls
    
    
class Control(object):
    def __init__(self,mapping, ctype, name, digital, sensitivity = 1):
        self.__name = name
        self.__ctype = ctype
        self.__digital = digital
        self.__mapping = mapping
        self.__state = 0
        self.__sensitivity = sensitivity
        
    def __repr__(self):
        return self.__str__()
    
        
    def __str__(self):
        return "<Control Name: {0}, Mapping: {1}, Type: {2}, State: {3}>".format(self.__name,self.__mapping, self.__ctype, self.__state)
    
    def set_state(self,state):
        self.__state = state
    
    def get_state(self):
        return self.__state
    
    def get_type(self):
        return self.__ctype

    def get_name(self):
        return self.__name
    
    def get_mapping(self):
        return self.__mapping
    
    def get_digital(self):
        return self.__digital
    
    def get_sensitivity(self):
        return self.__sensitivity

    
if __name__ == "__main__":

    Program = GSEF()
    #If the program creates an error, make a popup window about it and close the program
    if not Program.ErrorMsg:
        Program.Run()
    else:
        popup = ErrorPopupWindow("Error",Program.ErrorMsg)
        popup.connect("destroy", Gtk.main_quit)
        popup.show_all()
        Gtk.main()
        
