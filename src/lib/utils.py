import os

def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False