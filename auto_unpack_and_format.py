import os
import shutil
import zipfile
import subprocess
import sys

def extract_asar(file_path, out_dir):
    # 需要提前：npm install -g asar
    cmd = ["asar", "extract", file_path, out_dir]
    print("正在解包ASAR...")
    subprocess.run(cmd, check=True)

def extract_zip(file_path, out_dir):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(out_dir)

def format_js_files(root_dir):
    print("正在格式化JS源码...")
    # Collect all JS files first
    js_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(subdir, file))
    
    # Batch process all JS files in a single subprocess call
    if js_files:
        try:
            subprocess.run(["js-beautify", "-r"] + js_files, check=True)
        except FileNotFoundError:
            print("Warning: js-beautify not found. Please install it: npm install -g js-beautify")
        except subprocess.CalledProcessError as e:
            print(f"Warning: js-beautify failed: {e}")

def extract_from_exe(file_path, out_dir):
    print("尝试从exe二进制中提取asar...")
    # Use streaming to avoid loading entire file into memory
    chunk_size = 1024 * 1024  # 1MB chunks
    search_pattern = b'{"files":'
    buffer = b''
    offset = 0
    found_idx = -1
    
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            # Search in buffer + new chunk
            search_data = buffer + chunk
            idx = search_data.find(search_pattern)
            
            if idx != -1:
                found_idx = offset + idx
                break
            
            # Keep last portion of buffer for pattern that might span chunks
            buffer = search_data[-len(search_pattern):]
            offset += len(chunk)
    
    if found_idx != -1:
        asar_start = max(0, found_idx - 16)
        out_file = os.path.join(out_dir, "extracted.asar")
        
        # Stream the extraction
        with open(file_path, "rb") as f:
            f.seek(asar_start)
            with open(out_file, "wb") as nf:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    nf.write(chunk)
        
        extract_asar(out_file, os.path.join(out_dir, "from_asar"))
    else:
        print("未找到asar头部，请手动分析。")

def main(pkg_path):
    workdir = "./unpack_result"
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir, exist_ok=True)
    ext = os.path.splitext(pkg_path)[1].lower()

    if ext == ".asar":
        extract_asar(pkg_path, workdir)
        format_js_files(workdir)
    elif ext == ".zip":
        extract_zip(pkg_path, workdir)
        format_js_files(workdir)
    elif ext == ".exe":
        extract_from_exe(pkg_path, workdir)
    else:
        print("不支持的文件类型，请自行处理。")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_unpack_and_format.py 你的包文件")
        sys.exit(1)
    main(sys.argv[1])