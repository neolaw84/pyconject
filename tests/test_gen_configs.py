import unittest

from pyconject import pyconject, generate_config


class TestGenerateConfig(unittest.TestCase):
    def test_generate_config_by_caller(self):
        from my_package.my_module import my_function

        config_dict = generate_config(my_function)
        expected_config = {
            "my_package": {
                "my_module": {"my_function": {"param1": 1, "param2": "blar"}}
            }
        }
        self.assertEqual(config_dict, expected_config)

    def test_generate_config_by_decorator(self):
        from my_package.my_decorated_module import my_function

        config_dict = generate_config(my_function)
        expected_config = {
            "my_package": {
                "my_module": {"my_function": {"param1": 1, "param2": "blar"}}
            }
        }
        self.assertEqual(config_dict, expected_config)
