import sys
import os
from compressor import rle, hce, lz77, defl

# function to compress a single file
def compress_file(file_loc, algo, dest_dir, name):
    file = open(file_loc, "rb")
    data = file.read()
    file.close()

    # get file extension
    temp = file_loc.split(".")
    ext = "\n"
    if len(temp)>1:
        ext = "."+temp[1]+"\n"
    byte_str = data

    if(algo == "rle"):
        byte_str = rle.compressor(byte_str)
    elif(algo == "hce"):
        byte_str = hce.compressor(byte_str)
    elif(algo == "lz77"):
        byte_str = lz77.compressor(byte_str)
    elif(algo == "defl"):
        byte_str = defl.compressor(byte_str)
    
    byte_str = bytes([ord(x) for x in ext]) + byte_str
    name = name + ".zip_" + algo

    os.makedirs(dest_dir, exist_ok=True)
    file_dest = dest_dir + "/" + name
    
    with open(file_dest, "wb") as f:
        f.write((byte_str))

    return

# function to compress a folder
def compress_folder(dir_loc, algo, dest_dir, name):
    stack = [dir_loc]
    files_to_process = []
    base_path = os.path.abspath(dir_loc)

    # Iterative stack-based traversal
    while(len(stack) > 0):
        current_dir = stack.pop()
        with os.scandir(current_dir) as entries:
            for entry in entries:
                if entry.is_dir():
                    stack.append(entry.path)
                elif entry.is_file():
                    files_to_process.append(entry.path)

    # metadata construction
    parts = [
        str(len(files_to_process)), '\n'
    ]
    
    byte_str_body = b""

    for file_path in files_to_process:
        file = open(file_path, "rb")
        data = file.read()
        file.close()

        byte_str = data
        if(algo == "rle"):
            byte_str = rle.compressor(byte_str)
        elif(algo == "hce"):
            byte_str = hce.compressor(byte_str)
        elif(algo == "lz77"):
            byte_str = lz77.compressor(byte_str)
        elif(algo == "defl"):
            byte_str = defl.compressor(byte_str)
        
        rel_path = os.path.relpath(file_path, base_path)
        comp_size = len(byte_str)

        parts.append(rel_path)
        parts.append('\n')
        parts.append(str(comp_size))
        parts.append('\n')
        
        byte_str_body = byte_str_body + byte_str

    parts.append('\n') # End of header marker
    metadata = "".join(parts)
    
    final_data = metadata.encode('latin-1') + byte_str_body
    
    name = name + ".zip_dir_" + algo
    os.makedirs(dest_dir, exist_ok=True)
    file_dest = dest_dir + "/" + name

    with open(file_dest, "wb") as f:
        f.write(final_data)

    return

# function to decompress a single file
def decompress_file(file_loc, dest_dir, name):
    algo = ""
    temp = file_loc.split(".")

    # get algorithm
    if(len(temp)>1):
        algo = temp[1][4:]

    file = open(file_loc, "rb")
    data = list(file.read())
    file.close()

    # get file extension
    ext = ""
    i = 0
    n = len(data)
    while(i<n and chr(data[i])!='\n'):
        ext = ext + str(chr(data[i]))
        i += 1
    comp = data[i+1:]
    byte_str = ""
    
    if(algo == "rle"):
        byte_str = rle.decompressor(comp)
    elif(algo == "hce"):
        byte_str = hce.decompressor(comp)
    elif(algo == "lz77"):
        byte_str = lz77.decompressor(comp)
    elif(algo == "defl"):
        byte_str = defl.decompressor(comp)

    name = name + ext
    os.makedirs(dest_dir, exist_ok=True)
    file_dest = dest_dir + "/" + name

    with open(file_dest, "wb") as f:
        f.write(byte_str)

    return

# function to decompress a folder
def decompress_folder(file_loc, dest_dir, name):
    algo = ""
    temp = file_loc.split(".")
    if len(temp) > 1:
        if temp[1].startswith("zip_dir_"):
            algo = temp[1][8:]
        elif temp[1].startswith("zip_"):
            algo = temp[1][4:]
        else:
            algo = temp[1]

    with open(file_loc, "rb") as f:
        data = f.read()

    # find header and body separator
    sep = b'\n\n'
    idx = data.find(sep)
    if idx == -1:
        header_bytes = data
        body = b""
    else:
        header_bytes = data[:idx]
        body = data[idx + 2 :]

    header = header_bytes.decode('latin-1')
    lines = header.split('\n')
    if not lines or lines[0] == '':
        return

    try:
        count = int(lines[0])
    except:
        return

    entries = []
    i = 1
    for _ in range(count):
        if i + 1 >= len(lines):
            break
        rel_path = lines[i]
        size = int(lines[i + 1])
        entries.append((rel_path, size))
        i += 2

    out_root = os.path.join(dest_dir, name)
    os.makedirs(out_root, exist_ok=True)

    pos = 0
    for rel_path, size in entries:
        comp_chunk = body[pos:pos + size]
        pos += size
        comp_list = list(comp_chunk)

        if algo == "rle":
            byte_str = rle.decompressor(comp_list)
        elif algo == "hce":
            byte_str = hce.decompressor(comp_list)
        elif algo == "lz77":
            byte_str = lz77.decompressor(comp_list)
        elif algo == "defl":
            byte_str = defl.decompressor(comp_list)
        else:
            byte_str = comp_chunk

        out_path = os.path.join(out_root, os.path.normpath(rel_path))
        parent = os.path.dirname(out_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(byte_str)

    return

# CLI usage
def usage():
    print("Usage:")
    print("  To compress:   cli.py <algo> <path> [dest_dir] [name]")
    print("                 algo: rle | hce | lz77 | defl")
    print("  To decompress: cli.py decompress <compressed_file> [dest_dir] [name]")
    sys.exit(1)

# helper to get default name from path
def _default_name_from_path(path):
    base = os.path.basename(path)
    if '.' in base:
        return base.split('.')[0]
    return base

# main function
def main():
    if len(sys.argv) < 3:
        usage()

    # parse command line arguments
    cmd = sys.argv[1]
    path = sys.argv[2]
    dest_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    name_arg = sys.argv[4] if len(sys.argv) > 4 else None

    # handle decompression
    if cmd.lower() == "decompress":
        if not os.path.isfile(path):
            raise Exception("Compressed file does not exist.")
        out_name = name_arg if name_arg is not None else _default_name_from_path(path)
        if ".zip_dir_" in os.path.basename(path) or ".zip_dir_" in path:
            decompress_folder(path, dest_dir, out_name)
        else:
            decompress_file(path, dest_dir, out_name)
        return

    # handle compression
    algo = cmd.lower()
    if algo not in ("rle", "hce", "lz77", "defl"):
        raise Exception(f"Unknown algorithm: {algo}")
        usage()

    if not os.path.exists(path):
        raise Exception("Input path does not exist.")

    out_name = name_arg if name_arg is not None else _default_name_from_path(path)

    if os.path.isdir(path):
        compress_folder(path, algo, dest_dir, out_name)
    else:
        compress_file(path, algo, dest_dir, out_name)

if __name__ == "__main__":
    main()
