from pathlib import Path 
from typing import List 

from unittest.mock import mock_open, Mock

def remove_file_or_directory(path: Path, force: bool = False):
    try:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            for child in path.iterdir():
                remove_file_or_directory(child, force)
            path.rmdir()
    except Exception as e:
        if not force:
            print(f"Error removing {path}: {e}")

def remove_files_or_directories(paths: List[Path], force: bool = False):
    for path in paths: 
        remove_file_or_directory(Path(path), force)

def _unique_str_gen(prefix="my_uniq_str"):
    for i in range(1000000):
        yield f"{prefix}_{str(i).zfill(7)}"

_unique_str = _unique_str_gen()

def get_dynamic_mock_open(args_to_read_data={"": ""}) -> Mock:
    def dynamic_mock_open(*args, **kwargs):
        return mock_open(read_data=args_to_read_data.get(args, None))(*args, **kwargs)
    return dynamic_mock_open