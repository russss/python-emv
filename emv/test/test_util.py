from unittest2 import TestCase
from emv.util import hex_int


class TestUtil(TestCase):
    def test_hex_int(self):
        self.assertEqual(hex_int(123456), [0x12, 0x34, 0x56])
        self.assertEqual(hex_int(65432), [0x06, 0x54, 0x32])
