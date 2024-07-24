import os
from unittest import TestCase
from unittest.mock import patch
import tempfile
from pathlib import Path
import yaml

from pyconject import pyconject

from tests.unittest_utils import get_dynamic_mock_open
from dev_p.dev_sp.dev_m import dev_func_2

class ClientUsageTest(TestCase):

    def setUp(self):
        self.configs = yaml.dump({
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
        self.configs_dev = yaml.dump({
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

    def test_vanilla(self):
        with self.assertRaises(TypeError):
            dev_func_2()

        a, b, c, d = dev_func_2(1, 2, 3)
        assert (a, b, c, d) == (1, 2, 3, "dev-default-in-func-definion")

    # def test_cntx_default(self):
    #     pyconject.init(globals())
    #     with pyconject.cntx():
    #         a, b, c, d = dev_func_2(1, 2)
    #         assert (a, b, c, d) == (1, 2, 303, 404)
    
    # def test_cntx_target_dev(self):
    #     with patch("builtins.open", get_dynamic_mock_open({
    #         (Path("./configs.yml"), "rt") : self.configs,
    #         (Path("./configs-dev.yml"), "rt") : self.configs_dev
    #     })):
    #         pyconject.init(globals())
    #         with pyconject.cntx(target="dev"):
    #             a, b, c, d = dev_func(1, 2)
    #             assert (a, b, c, d) == (1, 2, "clt-defined-in-configs-dev-c", "dev-default-in-func-definion")

    # def test_cntx_custom_cfg_files(self):
    #     with patch("builtins.open", get_dynamic_mock_open({
    #         (Path("./cfgs.yml"), "rt") : self.configs,
    #         (Path("./cfgs-dev.yml"), "rt") : self.configs_dev
    #     })):
    #         pyconject.init(globals())
    #         with pyconject.cntx(config_path="cfgs.yml"):
    #             a, b, c, d = dev_func(1, 2)
    #             assert (a, b, c, d) == (1, 2, "clt-defined-in-configs-c", "dev-default-in-func-definion")

    # def test_cntx_custom_cfg_files_target_dev(self):
    #     with patch("builtins.open", get_dynamic_mock_open({
    #         (Path("./cfgs.yml"), "rt") : self.configs,
    #         (Path("./cfgs-dev.yml"), "rt") : self.configs_dev
    #     })):
    #         pyconject.init(globals())
    #         with pyconject.cntx(config_path="cfgs.yml", target="dev"):
    #             a, b, c, d = dev_func(1, 2)
    #             assert (a, b, c, d) == (1, 2, "clt-defined-in-configs-dev-c", "dev-default-in-func-definion")
            
