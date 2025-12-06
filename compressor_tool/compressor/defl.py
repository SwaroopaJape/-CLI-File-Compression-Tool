from .lz77 import compressor as lz_compressor, decompressor as lz_decompressor
from .hce import compressor as hc_compressor, decompressor as hc_decompressor

# function to compress data using deflation: first LZ77, then HCE
def compressor(data):
    tokens = lz_compressor(data)
    return hc_compressor(tokens)

# function to decompress data using deflation: first HCE, then LZ77
def decompressor(data):
    tokens = hc_decompressor(data)
    return lz_decompressor(tokens)

