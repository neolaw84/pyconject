import os
from unittest import TestCase
from unittest.mock import patch
import tempfile
from pathlib import Path
import yaml

from pyconject import pyconject

from tests.unittest_utils import remove_files_or_directories, _unique_str, get_dynamic_mock_open
from dev_p.dev_sp.dev_m import dev_func

RELATIVE_PATH_TO = "./relative/path/to"

class ClientUsageTest(TestCase):

    def setUp(self):
        self.user_cwd = tempfile.TemporaryDirectory(dir="./")
        self.original_cwd = os.getcwd()
        os.chdir(self.user_cwd.name)
        super().setUp()

    def tearDown(self):
        remove_files_or_directories([
            "./configs.yml", 
            "./configs-dev.yml",
            "./configs-stg.yml", 
            "./configs-prd.yml",
            f"{RELATIVE_PATH_TO}/cfg.yml",
            f"{RELATIVE_PATH_TO}/cfg-dev.yml",
            f"{RELATIVE_PATH_TO}/cfg-stg.yml",
            f"{RELATIVE_PATH_TO}/cfg-prd.yml",
            self.user_cwd
        ])
        os.chdir(self.original_cwd)
        super().tearDown()

    def test_vanilla(self):
        with self.assertRaises(TypeError):
            dev_func()

        a, b, c, d = dev_func(1, 2, 3)
        assert (a, b, c, d) == (1, 2, 3, "dev-default-in-func-definion")

    def test_cntx_default(self):
        configs = yaml.dump({
            "dev_p": {
                "dev_sp": {
                    "dev_m": {
                        "dev_func": {
                            "b": "clt-defined-in-configs-b",
                            "c": "clt-defined-in-configs-c"
                        }
                    }
                }
            }
        })
        configs_dev = yaml.dump({
            "dev_p": {
                "dev_sp": {
                    "dev_m": {
                        "dev_func": {
                            "c": "clt-defined-in-configs-dev-c"
                        }
                    }
                }
            }
        })
        
        with patch("builtins.open", get_dynamic_mock_open({
            (Path("./configs.yml"), "rt") : configs,
            (Path("./configs-dev.yml"), "rt") : configs_dev
        })) as mock_file:
            global dev_func
            dev_func = pyconject.func(dev_func)
            with pyconject.cntx({}):
                a, b, c, d = dev_func(1, 2)
                assert (a, b, c, d) == (1, 2, "clt-defined-in-configs-c", "dev-default-in-func-definion")
