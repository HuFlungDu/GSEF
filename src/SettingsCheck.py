import os
import Globals
'''def check_settings(dictionary, XML, path = []):
    #print dictionary
    returnval = True
    for key, value in dictionary.items():
        newpath = path+[key]
        if type(value) == tuple:
            node = XML
            for item in path:
                if item != "":
                    node = node.find(item)
                    if node == None:
                        return False
            if key != "":
                node = node.find(key)
            if node == None:
                return False
            atts = []
            for AttName in value[0]:
                att = node.get(AttName)
                if att == None:
                    return False
                atts.append(att)
            returnval &= value[1](*atts)
        else:
            returnval &= check_settings(value,XML,newpath)
    return returnval'''

def check_settings(dictionary,XML):
    returnval = True
    if dictionary == None:
        return True
    for key,value in dictionary.items():
        NodeName = key[0]
        NodeCount = key[1]
        AttNames = key[2]
        CheckFunc = key[3]
        if NodeName == "":
            XMLNodes = [XML]
        else:
            XMLNodes = XML.findall(NodeName)
        if len(XMLNodes) != NodeCount and NodeCount != 0:
            return False
        for Node in XMLNodes:
            atts = []
            for AttName in AttNames:
                att = Node.get(AttName)
                if att == None:
                    return False
                atts.append(att)
            if CheckFunc:
                returnval &= CheckFunc(*atts)
            returnval &= check_settings(value,Node)
    return returnval
    
        
        

#Make sure the given path for directories in the settings file exists
def DirectoryPathSanityCheck(Path):
    if os.name != "posix":
        return os.path.isdir(Path)
    else:
        pathlist = Path.split("/")
        if pathlist[0] == "~":
            if len(pathlist) == 0:
                return os.path.isdir(Globals.homedir)
            else:
                return os.path.isdir(Globals.homedir+"".join(pathlist[1:]))
        else:
            return os.path.isdir(Path)

#Make sure the given preferred window heights are actually numbers
def WindowSizeSanityCheck(width,height):
    try:
        int(width)
        int(height)
        return True
    except:
        return False
def SystemNameSanityCheck(name):
    return ValidPathNameCheck(name)

def SystemExistSanityCheck(name):
    return DirectoryPathSanityCheck(Globals.DataDir+"Systems/System_"+name)

def ValidPathNameCheck(name):
    try:
        Globals.DataDir+"temp/"+name
        open(Globals.DataDir+"temp/"+name,'w').close()
        os.remove(Globals.DataDir+"temp/"+name)
        return True
    except Exception as e:
        return False

def CoreNameSanityCheck(name,systemname):
    return ValidPathNameCheck(name)
def CoreExistSanityCheck(name,systemname):
    if name == "(Default Core)":
        return True
    return DirectoryPathSanityCheck(Globals.DataDir+"Systems/System_"+systemname+"/Core_"+name)
def GameNameSanityCheck(name):
    return ValidPathNameCheck(name)
def GameSettingsSanityCheck(name, core, filename, system):
    return (os.path.isfile(Globals.DataDir+"Games/"+system+"/"+name+"/"+filename))
def PatchNameSanityCheck(name):
    return ValidPathNameCheck(name)