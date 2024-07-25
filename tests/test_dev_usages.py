import os
from unittest import TestCase
from unittest.mock import patch
import tempfile
from pathlib import Path
import yaml

# import pyconject as root_pyconject
from pyconject import pyconject

from unittest_utils import get_dynamic_mock_open
from dev_p.dev_sp.dev_m import dev_func, dev_func_sp, dev_func_m, dev_func_sp_custom, dev_func_sp_custom2

class DevUsageTest(TestCase):

    def test_vanilla(self):
        with self.assertRaises(TypeError):
            dev_func()

        a, b, c, d = dev_func(1, 2, 3)
        assert (a, b, c, d) == (1, 2, 3, "dev-default-in-func-definion")

    def test_cntx_default(self):
        pyconject.init(globals())
        with pyconject.cntx():
            a, b, c, d = dev_func(1, 2)
            assert (a, b, c, d) == (1, 2, 303, 404)

    def test_cntx_target_dev(self):
        pyconject.init(globals())
        with pyconject.cntx(target="dev"):
            a, b, c, d = dev_func(1, 2)
            assert (a, b, c, d) == (1, 2, 303, "404-dev")

    def test_cntx_default_sp(self):
        pyconject.init(globals())
        with pyconject.cntx():
            a, b, c, d = dev_func_sp(1, 2)
            assert (a, b, c, d) == (1, 2, 3003, 404)

    def test_cntx_target_dev_sp(self):
        pyconject.init(globals())
        with pyconject.cntx(target="dev"):
            a, b, c, d = dev_func_sp(1)
            assert (a, b, c, d) == (1, 2002, "3003-dev", "404-dev")

    def test_cntx_default_m_func(self):
        pyconject.init(globals())
        with pyconject.cntx():
            a, b, c, d = dev_func_m()
            assert (a, b, c, d) == (100001, 20002, 3003, 404)

    def test_cntx_default_m_func_custom(self):
        pyconject.init(globals())
        with pyconject.cntx():
            a, b, c, d = dev_func_sp_custom()
            assert (a, b, c, d) == (11, 22, "c", "d")

    def test_cntx_default_m_func_custom2(self):
        pyconject.init(globals())
        with pyconject.cntx(target="dev"):
            a, b, c, d = dev_func_sp_custom2()
            assert (a, b, c, d) == (111, 22, "cc", "dd")

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
            
