import os
import shutil
import zipfile
import subprocess
import sys

def is_asar(file_path):
    with open(file_path, "rb") as f:
        magic = f.read(4)
        return magic == b'\x04\x00\x00\x00' or file_path.endswith('.asar')

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
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.js'):
                src_path = os.path.join(subdir, file)
                # 用js-beautify
                subprocess.run(["js-beautify", "-r", src_path])  # -r覆盖原文件

def extract_from_exe(file_path, out_dir):
    print("尝试从exe二进制中提取asar...")
    with open(file_path, "rb") as f:
        data = f.read()
    idx = data.find(b'{"files":')  # 粗略，需更智能处理as力as头
    if idx != -1:
        out_file = os.path.join(out_dir, "extracted.asar")
        with open(out_file, "wb") as nf:
            nf.write(data[idx-16:])
        extract_asar(out_file, os.path.join(out_dir, "from_asar"))
    else:
        print("未找到asar头部，请手动分析。")

def main(pkg_path):
    workdir = "./unpack_result"
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir, exist_ok=True)
    ext = os.path.splitext(pkg_path)[1]

    if ext == ".asar" or is_asar(pkg_path):
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