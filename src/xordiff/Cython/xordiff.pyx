cimport numpy as np
import numpy as np
cimport cython

@cython.boundscheck(False)
def numpyxor(np.ndarray[np.uint8_t, ndim=1] n1, np.ndarray[np.uint8_t, ndim=1] n2, unsigned int size):
    cdef np.ndarray[np.uint8_t, ndim=1] h = np.empty(size, dtype=np.uint8)
    cdef np.ndarray[np.uint_t, ndim=1] retoff = np.empty(size, dtype=np.uint)
    cdef unsigned int i = 0, j = 0, offsets_size = 1, state = 0
    retoff[0] = 0

    while i < size:
            if state == 0:
                if n1[i] == n2[i]:
                    retoff[offsets_size] = i
                    offsets_size += 1
                    state = 1
                else:
                    h[j] = n1[i]
                    j += 1

            elif state == 1:
                if n1[i] != n2[i]:
                    h[j] = n1[i]
                    j += 1
                    retoff[offsets_size] = i
                    offsets_size += 1
                    state = 0
            i+=1
    if state == 0:
        retoff[offsets_size] = i
        offsets_size += 1
    retoff.resize(offsets_size, refcheck=False)
    h.resize(j, refcheck=False)
    return h,retoff

@cython.boundscheck(False)
def numpyundif(np.ndarray[np.uint8_t, ndim=1] n1, np.ndarray[np.uint8_t, ndim=1] n2, np.ndarray[np.uint_t, ndim=1] offsets):
    cdef np.ndarray[np.uint8_t, ndim=1] retarr = n2.copy()
    cdef unsigned int i = 0, j = 0, n1off = 0, start = 0, stop = 0, size = offsets.size
    while i < size:
        start = offsets[i]
        j = start
        stop = offsets[i+1]
        while j < stop:
            retarr[j] = n1[n1off]
            n1off += 1
            j += 1
        i += 2
    return retarr
