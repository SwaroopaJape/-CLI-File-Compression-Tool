from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("compressor.hce", ["compressor/hce.pyx"]),
    Extension("compressor.lz77", ["compressor/lz77.pyx"]),
    Extension("compressor.rle", ["compressor/rle.pyx"]),
]

setup(
    name="compressor",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
)
