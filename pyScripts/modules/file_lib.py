'''Library class that holds general functionality such as file
   manipulation, terminal commands etc.
'''
import os
import glob
import json
from bson import json_util

def json_dump(data, filename):
    try:
        with open(filename, 'w') as out:
            json.dump(data, out, indent=4, default=json_util.default)

        print(f"Successfully dumped data to {filename}.")
        return True
    except Exception as e:
        return e


def ls_dir(path, extension="csv"):
    try:
        return glob.glob(os.path.join(path, f"*.{extension}"))
    except Exception as e:
        return e


def split_path(file_path):
    path = os.path.dirname(file_path)
    filename = os.path.basename(file_path)

    return path, filename