# cython: boundscheck=False, wraparound=False

# function to comvert data to string and return bytes of rle encoding
def compressor(bytes data):
    cdef int n = len(data)
    if n == 0:
        return b""
    
    cdef unsigned char curr = data[0]
    cdef int count = 1
    cdef list comp = []
    cdef int i
    cdef unsigned char byte

    for i in range(1, n):
        byte = data[i]
        if byte == curr and count < 255:  # Limit count to fit in byte
            count += 1
        else:
            comp.append(curr)
            comp.append(count)
            curr = byte
            count = 1
    
    comp.append(curr)
    comp.append(count)
    
    return bytes(comp)

# get back the actual data from byte data
def decompressor(data):
    cdef list tokens = list(data) if not isinstance(data, list) else data
    cdef int n = len(tokens)
    cdef int i = 0
    cdef list result = []
    cdef unsigned char byte
    cdef int count, j

    while i < n - 1:
        byte = tokens[i]
        count = tokens[i + 1]
        for j in range(count):
            result.append(byte)
        i += 2

    return bytes(result)
