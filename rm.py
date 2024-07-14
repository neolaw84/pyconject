import argparse
from pathlib import Path
from glob import glob

def remove_file_or_directory(path: Path, force: bool = False):
    """
    Removes a file or directory recursively if it exists.
    :param path: Path to the file or directory.
    :param force: If True, suppresses error messages.
    """
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


def main():
    parser = argparse.ArgumentParser(description="Emulating linux' `rm` command.")
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Remove directories recursively"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Suppress error messages"
    )
    parser.add_argument(
        "paths", nargs="+", help="Paths to files or directories to delete"
    )
    args = parser.parse_args()

    for path_str in args.paths:
        path = Path(path_str)
        for p in glob(path):
            remove_file_or_directory(p, force=args.force)


if __name__ == "__main__":
    main()
