from .lz77 import compressor as lz_compressor, decompressor as lz_decompressor
from .hce import compressor as hc_compressor, decompressor as hc_decompressor

def compressor(data):
    tokens = lz_compressor(data)
    return hc_compressor(tokens)

def decompressor(data):
    tokens = hc_decompressor(data)
    return lz_decompressor(tokens)

# test
# A =  "Lorem ipsum dolor sit amet. Ut internos quia sed quam rerum sit suscipit maiores ea facere quod. Hic maxime maiores ut modi cupiditate ut ipsum voluptate. Aut autem numquam ut illum odit quo fugit necessitatibus. Qui facere magnam ut quod repellendus est debitis quibusdam qui cumque quia."
# B = compressor(A.encode('latin-1'))
# C = decompressor(B).decode('latin-1')

# print(C==A)