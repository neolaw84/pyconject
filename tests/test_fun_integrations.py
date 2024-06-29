import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path
from glob import glob

from pyconject import pyconject, reset, resolve


class TestFunIntegrations(unittest.TestCase):

    def setUp(self) -> None:
        reset()
        return super().setUp()
    
    def tearDown(self) -> None:
        for f in glob("./tmp*.yml"):
            Path(f).unlink(missing_ok=True)
        return super().tearDown()
    
    def test_by_decorator(self):
        # when the decorator is used, the given configs.yaml
        # should overwrite the default parameter values
        with patch(
            "builtins.open",
            unittest.mock.mock_open(
                read_data="""
                my_package:
                    my_decorated_module: 
                        my_function: 
                            param1: 100
                """
                    ),
                ):
            from my_package.my_decorated_module import my_function

            param1, param2 = my_function()
            self.assertEqual(param1, 100)
            self.assertEqual(param2, "blar")

    def test_by_decorator_no_configs(self):
        # when no configs.yml present and user specifies nothing, 
        # it shouldn't throw an Exception
        from my_package.my_decorated_module import my_function

        param1, param2 = my_function(200)
        self.assertEqual(param1, 200)
        self.assertEqual(param2, "blar")

    def test_by_decorator_no_configs_file_when_user_specified(self):
        # when no configs.yml present and user specifies it, 
        # it should throw an Exception
        with self.assertRaises(FileNotFoundError):
            from my_package.my_decorated_module import my_function
            resolve(filename="./configs.yml")
            my_function(200)
        

    def test_by_decorator_with_dev_configs(self):
        # when the decorator is used, the developer's configs.yml
        # should be used for function calls
        from my_package.my_decorated_module import my_function_with_no_default_value as my_func

        ps = my_func()
        self.assertTupleEqual(ps, (1, 2, 3, 4))

    def test_by_decorator_with_dev_configs_user_configs(self):
        # when the decorator is used, the user's configs.yml
        # should override developer's configs.yml
        import yaml
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".yml", dir="./", delete=False) as cfg:
            yaml.dump({"my_package": {
                        "my_decorated_module": 
                            {"my_function_with_no_default_value":{ 
                                "param1": 100, "param2": 200
                            }}}}, cfg
                )
            to_delete = cfg.name
        from my_package.my_decorated_module import my_function_with_no_default_value as my_func
        resolve(filename=to_delete)
        ps = my_func()
        self.assertTupleEqual(ps, (100, 200, 3, 4))


    def test_by_caller(self):
        # when explicitly wrapped, the given configs.yaml
        # should overwrite the default parameter values
       
        with patch(
            "builtins.open",
            unittest.mock.mock_open(
                read_data="""
                my_package:
                    my_module: 
                        my_function: 
                            param1: 100
                """
                    ),
                ):
            from my_package.my_module import my_function

            my_function = pyconject(
                my_function
            )  # this call should replace the my_function with wrapped_function
            param1, param2 = my_function()
            self.assertEqual(param1, 100)
            self.assertEqual(param2, "blar")
