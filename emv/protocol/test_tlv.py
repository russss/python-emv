# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from ..util import unformat_bytes
from .tlv import TLV


class TestTLV(TestCase):
    def test_tlv(self):
        data = unformat_bytes('6F 1D 84 07 A0 00 00 00 03 80 02 A5 12 50 08 42 41 52 43 4C 41 59 53 87 01 00 5F 2D 02 65 6E')
        tlv = TLV.unmarshal(data)
        print(tlv)

        data = unformat_bytes('77 1E 9F 27 01 80 9F 36 02 00 05 9F 26 08 6E CF 93 47 C1 A9 24 71 9F 10 07 06 0B 0A 03 A4 90 00')
        tlv = TLV.unmarshal(data)
        print(tlv)

