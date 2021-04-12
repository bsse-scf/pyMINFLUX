from unittest import TestCase
import pyminflux


class TestFundamentals(TestCase):
    def test_version(self):
        self.assertTrue(pyminflux.__version__ != "")
