import os
import shutil
import zlib


def read_string(loc, length):
    return open(loc, "r").read(length)


def read_char(loc):
    return read_string(loc, 1)


def read_file(loc):
    return open(loc, "r")


def zipfolder(file_name, folder):
    shutil.make_archive(file_name, "zip", folder)


def unzipfolder(filename, destination):
    shutil.unpack_archive(filename, destination)


def get_path(file):
    directory_path, filename = os.path.split(file)
    return directory_path


def crc32(target, chunksize=65536):
    with open(target, "rb") as f:
        checksum = 0
        while chunk := f.read(chunksize):
            checksum = zlib.crc32(chunk, checksum)
        return checksum


def get_file_list(target):
    file_paths = []
    for root, dirs, files in os.walk(target):
        for name in files:
            file_path = os.path.join(root, name)
            file_paths.append(file_path)
    return file_paths


def copy_dirtree(src, dst):
    src = os.path.abspath(src)
    src_prefix = len(src) + len(os.path.sep)
    try:
        for root, dirs, files in os.walk(src):
            for dirname in dirs:
                dirpath = os.path.join(dst, root[src_prefix:], dirname)
                os.mkdir(dirpath)
    except:
        pass


def get_filesize(file):
    try:
        size = os.path.getsize(file)
        if type(size) is type(None):
            return 0
        return size
    except Exception:
        return 0


def join_paths(root, dir):
    return os.path.join(root, dir)


def get_curdir():
    return os.curdir


def create_directory(dir):
    try:
        os.mkdir(dir)
    except:
        pass


def remove_file(file):
    try:
        os.remove(file)
    except:
        pass


def copy_file(src, dst):
    try:
        shutil.copy(src, dst)
    except:
        pass


def get_filename(file):
    return os.path.basename(file)


def get_fileext(file):
    ext = os.path.splitext(os.path.basename(file))
    return ext[1].lower()


def move_file(src, dst):
    try:
        os.replace(src, dst)
    except:
        pass


def clear_folder(folder):
    try:
        shutil.rmtree(folder)
    except OSError:
        pass


def write_to_file(file, msg=None):
    try:
        with open(file, "a") as f:
            f.write("{}\n".format(msg))
    except Exception:
        open(file, "w").write(msg)


def check_file_exists(file):
    try:
        if os.path.exists(file):
            return True
        else:
            return False
    except OSError:
        pass
