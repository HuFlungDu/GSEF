cimport numpy as np
import numpy as np
cimport cython

@cython.boundscheck(False)
def numpyxor(np.ndarray[np.uint8_t, ndim=1] n1, np.ndarray[np.uint8_t, ndim=1] n2, int size):
    cdef np.ndarray[np.uint8_t, ndim=1] h = np.empty(size, dtype=np.uint8)
    cdef np.ndarray[np.uint_t, ndim=1] retoff
    cdef int i = 0
    cdef int j = 0
    cdef char state = 0
    cdef char xor = 0
    cdef int off = 0
    cdef int length = 0
    offsets = [0]
    
    while i < size:
            if state == 0:
                xor = n1[<unsigned int>i] ^ n2[<unsigned int>i]
                h[<unsigned int>j] = xor
                if xor == 0:
                    state = 1
                j += 1
                
            elif state == 1:
                xor = n1[<unsigned int>i] ^ n2[<unsigned int>i]
                if xor != 0:
                    h[j] = xor
                    j += 1
                    offsets.append(i)
                    state = 0
            i+=1
    retoff = np.array(offsets,dtype=np.uint)
    h.resize(j, refcheck=False)
    return h,retoff
        
@cython.boundscheck(False)
def numpyundif(np.ndarray[np.uint8_t, ndim=1] n1, np.ndarray[np.uint8_t, ndim=1] n2, np.ndarray[np.uint_t, ndim=1] offsets):
    cdef np.ndarray[np.uint8_t, ndim=1] retarr = n2.copy()
    cdef int i = 0
    cdef int n1off = 0
    cdef int off = 0
    while i < n1.size:
        if n1[<unsigned int>i] == 0:
            off += 1
            n1off = 0
        else:
            retarr[<unsigned int>(offsets[<unsigned int>off]+n1off)] ^= n1[<unsigned int>i]
            n1off += 1
        i += 1
    
    return retarr