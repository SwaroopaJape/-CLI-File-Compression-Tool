# cython: boundscheck=False, wraparound=False

import heapq
from collections import Counter

cdef class Node:
    cdef public object char
    cdef public int freq
    cdef public Node left
    cdef public Node right
    
    def __init__(self, character, int freq):
        self.char = character
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, Node other):
        return self.freq < other.freq

def build_huffman_tree(str text):
    freq_hm = Counter(text)
    cdef list heap = [Node(ch, f) for ch, f in freq_hm.items()]
    heapq.heapify(heap)
    cdef Node left, right, merged

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heapq.heappop(heap)

def char_to_bit(Node node):
    # Generate Huffman codes via tree traversal
    cdef list waiting = [(node, "")]
    cdef dict code = {}
    cdef Node curr
    cdef str coding
    
    while waiting:
        curr, coding = waiting.pop()
        if curr.left is None:
            code[curr.char] = coding
        else:
            waiting.append((curr.left, coding + "0"))
            waiting.append((curr.right, coding + "1"))
    return code

def bin_to_byte(str bin_str):
    # Convert binary string to bytes
    cdef int pad_len = (8 - len(bin_str) % 8) % 8
    bin_str += "0" * pad_len
    cdef bytearray byte_arr = bytearray()
    cdef int i
    
    for i in range(0, len(bin_str), 8):
        byte_arr.append(int(bin_str[i:i+8], 2))
    
    return bytes(byte_arr)

def byte_to_bin(bytes byte_str, int og_len):
    cdef list parts = []
    cdef unsigned char c
    
    for c in byte_str:
        parts.append(f"{c:08b}")
    
    cdef str bin_str = "".join(parts)
    return bin_str[:og_len]

def encode(str text, dict code):
    cdef list parts = []
    cdef str char
    
    for char in text:
        parts.append(code[char])
    
    return "".join(parts)

def decode(str bin_str, dict code):
    cdef dict decoder = {v: k for k, v in code.items()}
    cdef str temp = ""
    cdef list result = []
    cdef str bit
    
    for bit in bin_str:
        temp += bit
        if temp in decoder:
            result.append(decoder[temp])
            temp = ""
    
    return "".join(result)

def compressor(data):
    cdef str text
    if isinstance(data, bytes):
        text = data.decode('latin-1')
    else:
        text = data
    
    cdef Node tree = build_huffman_tree(text)
    cdef dict coder = char_to_bit(tree)
    cdef str bin_str = encode(text, coder)
    
    # Build metadata
    cdef list parts = [
        str(len(bin_str)), '\n',
        str(len(coder)), '\n'
    ]
    
    cdef str k, v
    for k, v in coder.items():
        parts.extend([str(ord(k)), '\n', v, '\n'])
    
    parts.append('\n')
    cdef str metadata = "".join(parts)
    cdef bytes compressed_data = bin_to_byte(bin_str)
    
    return metadata.encode('latin-1') + compressed_data

def decompressor(data):
    cdef bytes byte_data = bytes(data) if not isinstance(data, bytes) else data
    cdef str byte_string = byte_data.decode('latin-1')
    cdef int meta_end = byte_string.find('\n\n')
    cdef bytes payload = byte_string[meta_end + 2:].encode('latin-1')

    # Parse metadata
    cdef list temp = byte_string[:meta_end].split("\n")
    cdef int og_len = int(temp[0])
    cdef int coder_len = int(temp[1])
    cdef dict coder = {}
    cdef int i = 2
    cdef int n = 2 + coder_len * 2
    
    while i < n:
        coder[chr(int(temp[i]))] = temp[i + 1]
        i += 2
    
    cdef str bin_str = byte_to_bin(payload, og_len)
    cdef str text = decode(bin_str, coder)
    
    return text.encode('latin-1')
