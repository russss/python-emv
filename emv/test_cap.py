# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from .protocol.response import RAPDU
from .util import unformat_bytes
from .cap import get_cap_value


class TestCAP(TestCase):
    def test_pinsentry_equivalence(self):
        # Real response from barclays-pinsentry.c, with its calculated response
        data = unformat_bytes('80 12 80 09 5F 0F 9D 37 98 E9 3F 12 9A 06 0A 0A 03 A4 90 00 90 00')
        res = RAPDU.unmarshal(data)
        self.assertEqual(get_cap_value(res), 46076570)
