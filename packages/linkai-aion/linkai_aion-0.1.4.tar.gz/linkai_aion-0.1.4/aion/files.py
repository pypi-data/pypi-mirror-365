from pathlib import Path
import shutil
from datetime import datetime

import zipfile


def read_file(path):
    return Path(path).read_text()


def write_file(path, text):
    Path(path).write_text(text)


def append_to_file(path, text):
    with open(path, "a") as f:
        f.write(text)


def get_file_extension(path):
    return Path(path).suffix


def get_file_size(path):
    return Path(path).stat().st_size


def get_file_name(path):
    return Path(path).name


def get_file_created_time(path):
    timestamp = Path(path).stat().st_ctime
    return datetime.fromtimestamp(timestamp)


def get_file_modified_time(path):
    modified_timestamp = Path(path).stat().st_mtime
    return datetime.fromtimestamp(modified_timestamp)


def zip_file(path, zip_path):
    path = Path(path)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if path.is_file():
            zipf.write(path, arcname=path.name)
        elif path.is_dir():
            for file in path.rglob('*'):
                if file.is_file():
                    zipf.write(file, arcname=file.relative_to(path))


def unzip_file(zip_path, extract_to):
    zip_path = Path(zip_path)
    extract_to = Path(extract_to)
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)


def is_file_empty(path):
    return Path(path).stat().st_size == 0


def list_files(dir_path):
    return [str(p) for p in Path(dir_path).iterdir() if p.is_file()]


def list_files_recursive(path):
    return [str(p) for p in Path(path).rglob("*") if p.is_file()]


def copy_file(src, dest):
    shutil.copy(src, dest)


def move_file(src, dest):
    shutil.move(src, dest)


def delete_file(path):
    Path(path).unlink()


def search_in_file(path, text):
    lines = Path(path).read_text().splitlines()
    return [line for line in lines if text in line]


def replace_in_file(path, find, replace):
    content = Path(path).read_text()
    Path(path).write_text(content.replace(find, replace))


def file_line_count(path):
    return len(Path(path).read_text().splitlines())


def file_word_count(path):
    return len(Path(path).read_text().split())


def split_file(path, n):
    lines = Path(path).read_text().splitlines()
    size = len(lines) // n
    return [lines[i * size:(i + 1) * size] for i in range(n)]
