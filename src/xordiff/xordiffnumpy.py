import numpy as np
import _xordiff

class numpyxor(object):
    def __init__(self,n1,n2):
        self.diffarr, self.offsets = _xordiff.numpyxor(n1,n2,n1.size)
        self.size = self.diffarr.size + self.offsets.size
        self.nbytes = self.diffarr.nbytes + self.offsets.nbytes
        
    def undiff(self,n2):
        return _xordiff.numpyundif(self.diffarr,n2,self.offsets)