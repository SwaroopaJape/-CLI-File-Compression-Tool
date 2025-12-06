
# File Compressor Tool

A command–line file compression utility supporting multiple classic compression algorithms — **RLE**, **Huffman (HCE)**, **LZ77**, and **DEFLATE**.  
The tool allows you to compress individual files or whole directories and stores the output in a user-specified folder.

---

## Features

- Multiple compression algorithms:
  - **RLE** (Run Length Encoding)
  - **HCE** (Huffman Coding Encoder)
  - **LZ77**
  - **DEFLATE** (LZ77 + Huffman)
- Compress **single files** or **entire folders**
- Automatically assigns output filenames
- All algorithms operate on raw bytes (`rb` mode)
- Cython-accelerated implementations (`.so` or `.c` files)
- Includes the **Canterbury Corpus** for benchmarking

---

## Project Structure

file_compressor_tool_project/  
│  
├── compressor_tool/  
│ ├── cli.py # Command-line interface  
│ └── compressor/ # Algorithm implementations  
│     ├── rle.pyx* # RLE encoder/decoder (Cython/C)  
│     ├── hce.pyx* # Huffman encoder/decoder  
│     ├── lz77.pyx* # LZ77 encoder/decoder  
│     ├── defl.py # DEFLATE implementation  
│     └── \_\_init__.py   
└── canterbury-corpus-master/ # Benchmark dataset

## Running the Compressor Tool

### 1. Build the Cython Modules (Required)
Before using the compressor, run:

```bash
pip install cython
python3 compressor_tool/setup.py build_ext --inplace
# now run the tool
python3 compressor_tool/cli.py <path> <algo> <dest_dir> [output_name]