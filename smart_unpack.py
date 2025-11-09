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
    with open(file_path, "rb") as f:
        data = f.read()
    idx = data.find(b'{"files":')
    if idx != -1:
        asar_start = max(0, idx - 16)
        out_file = os.path.join(out_dir, "extracted.asar")
        with open(out_file, "wb") as nf:
            nf.write(data[asar_start:])
        extract_asar(out_file, os.path.join(out_dir, "from_asar"))
    else:
        print("未找到asar头部，请手动分析。")

def format_code(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(subdir, file)
            if file.endswith('.js'):
                subprocess.run(["js-beautify", "-r", path])
            elif file.endswith('.json'):
                subprocess.run(["prettier", "--write", path])
            elif file.endswith('.ts'):
                subprocess.run(["prettier", "--write", path])
            elif file.endswith('.css'):
                subprocess.run(["prettier", "--write", path])
            elif file.endswith('.html'):
                subprocess.run(["prettier", "--write", path])

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