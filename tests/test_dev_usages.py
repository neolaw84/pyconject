import os
from unittest import TestCase
from unittest.mock import patch
import tempfile
from pathlib import Path
import yaml

# import pyconject as root_pyconject
from pyconject import pyconject

from dev_p.dev_sp.dev_m import dev_func, dev_func_sp, dev_func_m, dev_func_sp_custom, dev_func_sp_custom2

class DevUsageTest(TestCase):

    def setUp(self):
        while(len(pyconject._cntx_stack.config_stack) > 0):
            pyconject._cntx_stack.config_stack.pop()
        while(len(pyconject._cntx_stack.target_stack) > 0):
            pyconject._cntx_stack.target_stack.pop()

    def test_vanilla(self):
        # this should not raise any exception
        a, b, c, d = dev_func()
        assert (a, b, c, d) == (101, 202, 303, 404)

        a, b, c, d = dev_func(1, 2, 3)
        assert (a, b, c, d) == (1, 2, 3, 404)

    def test_cntx_default(self):
        a, b, c, d = dev_func(1, 2)
        assert (a, b, c, d) == (1, 2, 303, 404)

    def test_cntx_target_dev(self):
        pyconject.init(globals())
        with pyconject.cntx(target="dev"):
            a, b, c, d = dev_func(1, 2)
            assert (a, b, c, d) == (1, 2, 303, "404-dev")

    def test_cntx_default_sp(self):
        a, b, c, d = dev_func_sp(1, 2)
        assert (a, b, c, d) == (1, 2, 3003, 404)

    def test_cntx_target_dev_sp(self):
        pyconject.init(globals())
        with pyconject.cntx(target="dev"):
            a, b, c, d = dev_func_sp(1)
            assert (a, b, c, d) == (1, 2002, "3003-dev", "404-dev")

    def test_cntx_default_m_func(self):
        a, b, c, d = dev_func_m()
        assert (a, b, c, d) == (100001, 20002, 3003, 404)

    def test_cntx_default_m_func_custom(self):
        a, b, c, d = dev_func_sp_custom()
        assert (a, b, c, d) == (11, 22, "c", "d")

    def test_cntx_default_m_func_custom2(self):
        pyconject.init(globals())
        with pyconject.cntx(target="dev"):
            a, b, c, d = dev_func_sp_custom2()
            assert (a, b, c, d) == (111, 22, "cc", "dd")

    