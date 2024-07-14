import unittest

from pyconject import pyconject, generate_config


class TestGenerateConfig(unittest.TestCase):
    def test_generate_config_by_caller(self):
        from pcj_b.pcj_bb import my_function

        config_dict = generate_config(my_function)
        expected_config = {
            "pcj_b": {
                "pcj_bb": {"my_function": {"param1": 1, "param2": "blar"}}
            }
        }
        self.assertEqual(config_dict, expected_config)

    def test_generate_config_by_decorator(self):
        from pcj_b.pcj_aa import my_function

        config_dict = generate_config(my_function)
        expected_config = {
            "pcj_b": {
                "pcj_aa": {"my_function": {"param1": 1, "param2": "blar"}}
            }
        }
        self.assertEqual(config_dict, expected_config)
