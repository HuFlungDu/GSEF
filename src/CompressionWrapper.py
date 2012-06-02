import gzip, bz2, zipfile, tarfile
import re

class NotImplementedYet(Exception):
    pass

#Generic info object, similar to tarfile.TarInfo
class ArchiveInfo(object):
    FILE = 0
    DIR = 1
    def __init__(self,name,size,mtime,mode,type,uid,gid,uname,gname,filetype):
        self.name = name
        self.size = size
        self.mtime = mtime
        self.mode = mode
        self.type = type
        self.uid = uid
        self.gid = gid
        self.uname = uname
        self.gname = gname
        self.filetype = filetype
    
    def isfile(self):
        return self.type == self.FILE
    def isdir(self):
        return self.type == self.DIR
        
#Generic wrapper for archives, mostly implements tarfile.TarFile
class Archive(object):
    TAR = 0
    ZIP = 1
    
    def __init__(self, filename, mode = 'r'):
        self.type = None
        self.open(filename,mode)
    
    def open(self,name, mode):
        if re.match(".*\.tar$", name):
            self.archive = tarfile.open(name, mode)
            self.type = self.TAR
        elif re.match(".*\.tar\.gz$", name):
            self.archive = tarfile.open(name, mode+':gz')
            self.type = self.TAR
        elif re.match(".*\.tar\.bz2$", name):
            self.archive = tarfile.open(name, mode+':bz2')
            self.type = self.TAR
        elif re.match(".*\.zip$", name):
            self.archive = zipfile.ZipFile(name, mode)
            self.type = self.ZIP
            
    def read(self,name):
        return [self.readtar,self.readzip][self.type](name)
    
    
    def readtar(self,name):
        readfile = self.archive.extractfile(name)
        returnstring = readfile.read()
        readfile.close()
        return returnstring
    def readzip(self,name):
        return self.archive.read(name)
    
    
            
    def getmember(self,name):
        return [self.getmembertar,self.getmemberzip][self.type](name)
    
    #Not fully implemented because I doubt I'll need it
    def getmembertar(self,name):
        tarinfo = self.archive.getmember(name)
        filetype = -1
        if tarinfo.is_file():
            filetype = ArchiveInfo.FILE
        elif tarinfo.is_dir():
            filetype = ArchiveInfo.DIR
        return ArchiveInfo(tarinfo.name,tarinfo.size,tarinfo.mtime,
                           tarinfo.mode,tarinfo.type,tarinfo.uid,
                           tarinfo.gid,tarinfo.uname,tarinfo.gname,filetype)
    def getmemberzip(self,name):
        raise NotImplementedYet
    
    
    def getmembers(self):
        return [self.getmemberstar,self.getmemberszip][self.type]()
    
    def getmemberstar(self):
        raise NotImplementedYet
    def getmemberszip(self):
        raise NotImplementedYet
    
    
    def getnames(self):
        return [self.getnamestar,self.getnameszip][self.type]()

    def getnamestar(self):
        return self.archive.getnames()
    def getnameszip(self):
        return self.archive.namelist()


    def list(self,verbose=True):
        return [self.listtar,self.listzip][self.type](verbose)

    def listtar(self,verbose=True):
        raise NotImplementedYet
    def listzip(self,verbose=True):
        raise NotImplementedYet
    

    def next(self):
        return [self.nextstar,self.nextzip][self.type]()

    def nexttar(self):
        raise NotImplementedYet
    def nextzip(self):
        raise NotImplementedYet

    def extractall(self,path=".", members=None):
        return self.archive.extractall(path, members)


    def extract(self, member, path=""):
        return self.archive.extract(member, path)

    def extractfile(self, member):
        return [self.extractfiletar,self.extractfilezip][self.type](member)

    def extractfiletar(self, member):
        return self.archive.extract(member)
    def extractfilezip(self, member):
        pass
        
    def close(self):
        return self.archive.close()
    
    def closetar(self):
        return self.archive.close()
    def closezip(self):
        pass