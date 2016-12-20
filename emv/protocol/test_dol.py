# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from ..util import unformat_bytes
from .dol import DOL


class TestDOL(TestCase):
    def test_dol(self):
        data = unformat_bytes('9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C 01 9F 37 04')
        dol = DOL.unmarshal(data)
        self.assertIn(0x9A, dol)
        self.assertEqual(dol[0x9A], 3)
        self.assertIn((0x9F, 0x37), dol)
        self.assertEqual(dol[(0x9F, 0x37)], 4)
