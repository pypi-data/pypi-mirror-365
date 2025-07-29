import atexit
import logging
import os
import shutil
import tempfile
import uuid

def read_if_exists(path, **kwargs):
    """
    Read the file if it exists, otherwise return None.
    """

    if (os.path.exists(path)):
        return read(path, **kwargs)

    return None

def read(path, strip = True, rstrip = True):
    with open(path, 'r') as file:
        contents = file.read()

    if (strip):
        contents = contents.strip()

    if (rstrip):
        contents = contents.rstrip()

    return contents

def write(path, contents):
    with open(path, 'w') as file:
        file.write(contents)

def write_avoid_collisions(path, contents):
    path = os.path.abspath(path)

    while (os.path.exists(path)):
        parts = os.path.splitext(path)
        new_path = parts[0] + '.0' + parts[1]
        log.warning("File collision detected. Instead of '%s', using '%s'." % (path, new_path))
        path = new_path

    write(path, contents)

def get_temp_path(prefix = '', suffix = '', rm = True, mkdir = True):
    """
    Get a path to a valid temp dirent.
    mkdir will determine if this directory will exist on return.
    If rm is True, then the dirent will be attempted to be deleted on exit
    (no error will occur if the path is not there).
    """

    path = None
    while ((path is None) or os.path.exists(path)):
        path = os.path.join(tempfile.gettempdir(), prefix + str(uuid.uuid4()) + suffix)

    if (mkdir):
        os.makedirs(path, exist_ok = True)

    if (rm):
        atexit.register(remove_dirent, path)

    return path

def remove_dirent(path):
    if (not os.path.exists(path)):
        return

    if (os.path.isfile(path) or os.path.islink(path)):
        os.remove(path)
    elif (os.path.isdir(path)):
        shutil.rmtree(path)
    else:
        raise ValueError("Unknown type of dirent: '%s'." % (path))

def copy_dirent(source, dest):
    """
    Copy a file or directory into dest.
    If source is a file, then dest can be a file or dir.
    If source is a dir, then dest must be a non-existent dir.
    """

    if (os.path.isfile(source)):
        shutil.copy2(source, dest)
    else:
        shutil.copytree(source, dest)
