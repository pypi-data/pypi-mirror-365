import unittest
from platform_utils import paths


class TestModulePath(unittest.TestCase):

    def test_module_path(self):
        self.assertTrue(paths.module_path().endswith('tests'))
