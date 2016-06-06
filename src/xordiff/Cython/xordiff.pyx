cimport numpy as np
import numpy as np
cimport cython

@cython.boundscheck(False)
def numpyxor(np.ndarray[np.uint8_t, ndim=1] n1, np.ndarray[np.uint8_t, ndim=1] n2, int size):
    cdef np.ndarray[np.uint8_t, ndim=1] h = np.empty(size, dtype=np.uint8)
    cdef np.ndarray[np.uint_t, ndim=1] retoff
    cdef int i = 0, j = 0, state = 0
    offsets = [0]

    while i < size:
            if state == 0:
                if n1[<unsigned int>i] == n2[<unsigned int>i]:
                    offsets.append(i)
                    state = 1
                else:
                    h[<unsigned int>j] = n1[<unsigned int>i]
                    j += 1

            elif state == 1:
                if n1[<unsigned int>i] != n2[<unsigned int>i]:
                    h[<unsigned int>j] = n1[<unsigned int>i]
                    j += 1
                    offsets.append(i)
                    state = 0
            i+=1
    if state == 0:
        offsets.append(i)
    retoff = np.array(offsets,dtype=np.uint)
    h.resize(j, refcheck=False)
    return h,retoff

@cython.boundscheck(False)
def numpyundif(np.ndarray[np.uint8_t, ndim=1] n1, np.ndarray[np.uint8_t, ndim=1] n2, np.ndarray[np.uint_t, ndim=1] offsets):
    cdef np.ndarray[np.uint8_t, ndim=1] retarr = n2.copy()
    cdef int i = 0, j = 0, n1off = 0, start = 0, stop = 0
    while i < offsets.size:
        off = start = offsets[i]
        stop = offsets[i+1]
        while j < stop:
            retarr[<unsigned int>j] = n1[<unsigned int>n1off]
            n1off += 1
            j += 1
        i += 2
    return retarr
