import sys

from datetime import datetime as dt

from unittest import TestCase
from pathlib import Path 
import tempfile
from importlib import import_module
from pyconject.configs import _get_dev_config_paths, ConfigPath

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

def _package_name_gen():
    # return f"my_package_{int(dt.now().timestamp()*1000)}"
    for i in range(1000000):
        yield f"my_package_{str(i).zfill(7)}"

_package_name = _package_name_gen()

class TestGetDevConfigPaths(TestCase):

    def setUp(self):
        # Create a temporary directory structure
        self.tempdir = Path(tempfile.mkdtemp(dir='./'))
        self.my_package = next(_package_name) # _package_name()
        self.package_dir = self.tempdir / self.my_package / 'my_sub_package'
        self.package_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files to make them valid packages
        (self.tempdir / self.my_package / '__init__.py').touch()
        (self.package_dir / '__init__.py').touch()
        
        # Create the module file
        self.module_file = self.package_dir / 'my_module.py'
        self.module_file.write_text("def my_func(a, b, c=3, d=4):\n    pass")
        
        # Add the temporary directory to the path
        sys.path.insert(0, str(self.tempdir))

    def tearDown(self):
        # Clean up the temporary directory and files
        # Note: shutil.rmtree is generally safer for deleting directories
        remove_file_or_directory(self.tempdir, force=True)

        # Remove the temporary directory from the path
        sys.path.remove(str(self.tempdir))

    def test_get_dev_config_paths(self):
        # Import the function after setting up the module
        # from my_package.my_sub_package.my_module import my_func  
        my_func = import_module(f"{self.my_package}.my_sub_package.my_module").my_func

        # Call the function and assert the result
        result = _get_dev_config_paths(my_func)
        
        expected = [
            ConfigPath({
                "": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'my_module-configs.yml'),
                "dev": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'my_module-configs-dev.yml'),
                "stg": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'my_module-configs-stg.yml'),
                "prd": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'my_module-configs-prd.yml'),
            }, f"{self.my_package}.my_sub_package.my_module", []),
            ConfigPath({
                "": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'pyconject.yml'), 
                "dev": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'pyconject-dev.yml'), 
                "stg": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'pyconject-stg.yml'), 
                "prd": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'pyconject-prd.yml'), 
            }, f"{self.my_package}.my_sub_package", []),
            ConfigPath({
                "": str(self.tempdir.absolute() / self.my_package / 'pyconject.yml'), 
                "dev": str(self.tempdir.absolute() / self.my_package / 'pyconject-dev.yml'), 
                "stg": str(self.tempdir.absolute() / self.my_package / 'pyconject-stg.yml'), 
                "prd": str(self.tempdir.absolute() / self.my_package / 'pyconject-prd.yml'), 
            }, self.my_package, [])
        ]
        for r, e in zip(result, expected):
            assert r == e
        # self.assertEqual(result, expected)

class TestGetDevConfigPathsCustom(TestCase):

    def setUp(self):
        # Create a temporary directory structure
        self.tempdir = Path(tempfile.mkdtemp(dir='./'))
        self.my_package = next(_package_name) # _package_name()
        self.package_dir = self.tempdir / self.my_package / 'my_sub_package'
        self.package_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files to make them valid packages
        (self.tempdir / self.my_package / '__init__.py').touch()
        (self.package_dir / '__init__.py').touch()
        with open (self.package_dir / "__init__.py", "wt") as f:
            f.write("pyconject='custom.yml'")
        
        # Create the module file
        self.module_file = self.package_dir / 'my_module.py'
        self.module_file.write_text("def my_func(a, b, c=3, d=4):\n    return a, b, c, d\npyconject='module-custom.yml'")
        
        # Add the temporary directory to the path
        sys.path.insert(0, str(self.tempdir))

    def tearDown(self):
        # Clean up the temporary directory and files
        # Note: shutil.rmtree is generally safer for deleting directories
        remove_file_or_directory(self.tempdir, force=True)

        # Remove the temporary directory from the path
        sys.path.remove(str(self.tempdir))

    def test_get_dev_config_paths_custom(self):
        # Import the function after setting up the module
        # from my_package.my_sub_package.my_module import my_func  
        my_func = import_module(f"{self.my_package}.my_sub_package.my_module").my_func

        # Call the function and assert the result
        result = _get_dev_config_paths(my_func)
        
        expected = [
            ConfigPath({
                "": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'module-custom.yml'),
                "dev": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'my_module-configs-dev.yml'),
                "stg": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'my_module-configs-stg.yml'),
                "prd": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'my_module-configs-prd.yml'),
            }, f"{self.my_package}.my_sub_package.my_module", [""]),
            ConfigPath({
                "": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'custom.yml'), 
                "dev": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'pyconject-dev.yml'), 
                "stg": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'pyconject-stg.yml'), 
                "prd": str(self.tempdir.absolute() / self.my_package / 'my_sub_package' / 'pyconject-prd.yml'), 
            }, f"{self.my_package}.my_sub_package", [""]),
            ConfigPath({
                "": str(self.tempdir.absolute() / self.my_package / 'pyconject.yml'), 
                "dev": str(self.tempdir.absolute() / self.my_package / 'pyconject-dev.yml'), 
                "stg": str(self.tempdir.absolute() / self.my_package / 'pyconject-stg.yml'), 
                "prd": str(self.tempdir.absolute() / self.my_package / 'pyconject-prd.yml'), 
            }, self.my_package, [])
        ]
        for r, e in zip(result, expected):
            assert r == e
        