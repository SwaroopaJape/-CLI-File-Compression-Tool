# cython: boundscheck=False, wraparound=False, cdivision=True

cdef int W = 4096
cdef int L = 255

# implementation of the lz77 algorithm encoding that converts the data to tokens and return bytes
def compressor(bytes data, int ws=W, int lb=L):
    cdef int n = len(data)
    cdef int i = 0
    cdef bytearray out = bytearray()
    cdef int h, best_len, best_off, pos, length
    cdef list table = [ [] for _ in range(4096) ]

    while i < n:
        if i + 2 < n:
            h = ((data[i] << 8) ^ (data[i+1] << 4) ^ data[i+2]) & 4095
        elif i + 1 < n:
            h = ((data[i] << 8) ^ (data[i+1] << 4)) & 4095
        else:
            h = 0

        best_len = 0
        best_off = 0

        for pos in table[h]:
            if pos >= i:
                break
            off = i - pos
            if off > ws:
                continue
            length = 0
            # Ensure we leave at least 1 byte for the literal at the end of the triple
            while length < lb and i + length < n - 1 and data[pos+length] == data[i+length]:
                length += 1
            if length > best_len:
                best_len = length
                best_off = off
                if best_len >= lb:
                    break

        table[h].append(i)
        if len(table[h]) > 64:
            table[h] = table[h][-64:]

        out.append(best_off >> 8)
        out.append(best_off & 0xFF)
        out.append(best_len)
        out.append(data[i + best_len])

        i += best_len + 1

    return bytes(out)

# get the original data back from the tokens
def decompressor(data):
    cdef bytearray out = bytearray()
    cdef int i = 0
    cdef int n = len(data)
    cdef int off, length, pos, j
    cdef bytes byte_data = bytes(data) if not isinstance(data, bytes) else data

    while i < n:
        off = (byte_data[i] << 8) | byte_data[i+1]
        length = byte_data[i+2]
        char_val = byte_data[i+3]
        i += 4

        if length > 0:
            pos = len(out) - off
            for j in range(length):
                out.append(out[pos + j])
        
        out.append(char_val)

    return bytes(out)
