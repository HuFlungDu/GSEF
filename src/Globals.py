import sys
import os
class game(object):
    def __init__(self,name,core):
        self.name = name
        self.core = core
        
    def __str__(self):
        return self.name
if os.name != "posix":
        from win32com.shell import shellcon, shell            #@UnresolvedImport
        homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
else:
    homedir = os.path.expanduser("~")+"/"
if not os.path.isdir(homedir+".GSEF"):
    os.mkdir(homedir+".GSEF")
homedir = homedir
DataDir = homedir + ".GSEF/"
SettingsXML = None
SystemXML = None
GamesXML = None
WindowHeight = 0
WindowWidth = 0
Systems = []
Cores = []
Games = {}
OpenWindows = 0
load_game = None
Controls = {}
Hotkeys = {}
system = None
Mainwindow = None
Mouse = None
Joysticks = None
OldJoystickStates = None
JoystickStates = None
StateData = []
StateSizes = []




def Update_Games():
    if len(GamesXML):
        for system in GamesXML.findall("System"):
            sysname = system.get("name")
            Games[sysname] = {}
            for Game in system.findall("Game"):
                gamename = Game.get("name")
                corename = Game.get("core")
                Games[sysname][game(gamename,corename)] = []
                for patch in Game.findall("Patch"):
                    Games[sysname][gamename].append(patch.get("name"))

WINDOWTYPE_MAINWINDOW = 0b1
WINDOWTYPE_MANAGESYSTEMS = 0b10
WINDOWTYPE_FILECHOOSER = 0b100
WINDOWTYPE_MAKEGAME = 0b1000
WINDOWTYPE_MANAGEGAMES = 0b10000
WINDOWTYPE_CONTROLS = 0b100000