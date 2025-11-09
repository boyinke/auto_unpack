import os
import shutil
import zipfile
import tarfile
import subprocess
import sys

def detect_file_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".asar":
        return "asar"
    elif ext in [".zip"]:
        return "zip"
    elif ext in [".tar", ".tar.gz", ".tgz"]:
        return "tar"
    elif ext == ".exe":
        return "exe"
    elif os.path.isdir(file_path):
        return "dir"
    return "unknown"

def extract_asar(file_path, out_dir):
    try:
        subprocess.run(["asar", "extract", file_path, out_dir], check=True)
    except Exception as e:
        print(f"asar extract failed: {e}")

def extract_zip(file_path, out_dir):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(out_dir)

def extract_tar(file_path, out_dir):
    with tarfile.open(file_path, 'r:*') as tar_ref:
        tar_ref.extractall(out_dir)

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

def format_code(root_dir):
    # Collect files by type for batch processing
    js_files = []
    prettier_files = []
    
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(subdir, file)
            if file.endswith('.js'):
                js_files.append(path)
            elif file.endswith(('.json', '.ts', '.css', '.html')):
                prettier_files.append(path)
    
    # Batch process JS files
    if js_files:
        print(f"Formatting {len(js_files)} JS files...")
        try:
            subprocess.run(["js-beautify", "-r"] + js_files, check=True)
        except FileNotFoundError:
            print("Warning: js-beautify not found. Please install it: npm install -g js-beautify")
        except subprocess.CalledProcessError as e:
            print(f"Warning: js-beautify failed: {e}")
    
    # Batch process prettier files
    if prettier_files:
        print(f"Formatting {len(prettier_files)} files with prettier...")
        try:
            subprocess.run(["prettier", "--write"] + prettier_files, check=True)
        except FileNotFoundError:
            print("Warning: prettier not found. Please install it: npm install -g prettier")
        except subprocess.CalledProcessError as e:
            print(f"Warning: prettier failed: {e}")

def main(pkg_path):
    workdir = "./unpack_result"
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir, exist_ok=True)
    t = detect_file_type(pkg_path)

    if t == "asar":
        extract_asar(pkg_path, workdir)
    elif t == "zip":
        extract_zip(pkg_path, workdir)
    elif t == "tar":
        extract_tar(pkg_path, workdir)
    elif t == "exe":
        extract_from_exe(pkg_path, workdir)
    elif t == "dir":
        workdir = pkg_path
        print("输入已是解压目录，直接格式化...")
    else:
        print("未知/暂不支持的文件类型。")
        return

    format_code(workdir)
    print(f"全部处理完成，结果在 {workdir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_unpack.py 你的包文件")
        sys.exit(1)
    main(sys.argv[1])