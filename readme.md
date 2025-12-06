# File Compressor Tool

A command-line file compression utility supporting multiple classic compression algorithms: **RLE**, **Huffman (HCE)**, **LZ77**, and **DEFLATE**.  
Compress individual files or entire directories with user-specified output locations.

---

## Features

- **Multiple compression algorithms:**
  - **RLE** (Run Length Encoding)
  - **HCE** (Huffman Coding Encoder)
  - **LZ77**
  - **DEFLATE** (LZ77 + Huffman)
- Compress **single files** or **entire folders**
- Automatic output filename generation
- Raw byte-level operations (`rb` mode)
- Cython-accelerated implementations
- Includes **Canterbury Corpus** for benchmarking

---

## Project Structure
```
file_compressor_tool_project/
│
├── compressor_tool/
│   ├── cli.py                    # Command-line interface
│   └── compressor/               # Algorithm implementations
│       ├── rle.pyx               # RLE encoder/decoder (Cython)
│       ├── hce.pyx               # Huffman encoder/decoder
│       ├── lz77.pyx              # LZ77 encoder/decoder
│       ├── defl.py               # DEFLATE implementation
│       └── __init__.py
├── test_benchmark.py             # benchmark tester
└── canterbury-corpus-master/     # Benchmark dataset
```

---

## Usage

### Step 1: Setup Cython Files
```bash
cd compressor_tool
pip install cython
python3 setup.py build_ext --inplace
cd ..
```

### Step 2: Run the Tool

**Compress:**
```bash
python3 compressor_tool/cli.py <algo> <path> [dest_dir] [name]
# algo: rle | hce | lz77 | defl
```

**Decompress:**
```bash
python3 compressor_tool/cli.py decompress <compressed_file> [dest_dir] [name]
```

### Step 3: Run Benchmark
```bash
python3 test_benchmark.py
```

---

## Examples
```bash
# Compress a file with DEFLATE
python3 compressor_tool/cli.py defl input.txt output/ myfile

# Compress a folder with Huffman
python3 compressor_tool/cli.py hce myfolder/ output/

# Decompress a file
python3 compressor_tool/cli.py decompress output/myfile.zip_defl restored/
```
