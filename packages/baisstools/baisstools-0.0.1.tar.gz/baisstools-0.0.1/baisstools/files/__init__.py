import os
from typing import Dict

def findpath(
    path    : str,
    base_dir: str            = None,
    result  : dict[str, str] = None,
    ) -> Dict[str, Dict]:
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    if not path.strip():
        raise ValueError("Path cannot be empty after stripping whitespace")
    if not os.path.exists(path):
        return result
    if result == None:
        result = {}
    result[path] = path
    if not base_dir:
        base_dir = path
    try   : files = os.listdir(path)
    except: files = []
    if not files:
        return (result)
    for basename in files:
        filename = os.path.realpath(os.path.join(path, basename))
        if filename != os.path.join(path, basename):
            # ignore symlinks
            continue
        findpath(
            path     = filename,
            base_dir = base_dir,
            result   = result
        )
        result[filename] = filename[len(path):].strip(os.sep)
    return result
