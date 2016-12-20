# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from ..util import unformat_bytes
from .structures import TLV, DOL


class TestTLV(TestCase):
    def test_tlv(self):
        data = unformat_bytes('''6F 1D 84 07 A0 00 00 00 03 80 02 A5 12 50 08 42 41 52 43 4C
                                 41 59 53 87 01 00 5F 2D 02 65 6E''')
        tlv = TLV.unmarshal(data)
        self.assertIn(0x50, tlv[0x6F][0xA5])

        data = unformat_bytes('''77 1E 9F 27 01 80 9F 36 02 00 05 9F 26 08 6E CF 93 47 C1 A9
                                 24 71 9F 10 07 06 0B 0A 03 A4 90 00''')
        tlv = TLV.unmarshal(data)
        self.assertIn((0x77), tlv)
        self.assertIn((0x9F, 0x26), tlv[0x77])
        self.assertEqual(tlv[0x77][(0x9F, 0x26)],
                         unformat_bytes('6E CF 93 47 C1 A9 24 71'))

        data = unformat_bytes('9F 17 01 03')
        tlv = TLV.unmarshal(data)
        self.assertEqual(tlv[(0x9F, 0x17)][0], 3)

    def test_nested_dol(self):
        # PAN has been doctored in this dump
        data = unformat_bytes('''70 68 8C 15 9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C
                                 01 9F 37 04 8D 17 8A 02 9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A
                                 02 9A 03 9C 01 9F 37 04 8E 0A 00 00 00 00 00 00 00 00 01 00 9F
                                 56 12 80 00 FF 00 00 00 00 00 01 FF FF 00 00 00 00 00 00 00 9F
                                 55 01 A0 5A 08 46 58 12 34 56 78 90 09 5F 34 01 00 9F 08 02 00
                                 01''')
        tlv = TLV.unmarshal(data)
        repr(tlv)
        self.assertIn(0x70, tlv)
        self.assertIs(type(tlv[0x70][0x8C]), DOL)


class TestDOL(TestCase):
    def test_dol(self):
        data = unformat_bytes('9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C 01 9F 37 04')
        dol = DOL.unmarshal(data)
        self.assertIn(0x9A, dol)
        self.assertEqual(dol[0x9A], 3)
        self.assertIn((0x9F, 0x37), dol)
        self.assertEqual(dol[(0x9F, 0x37)], 4)
        self.assertEqual(dol.size(), 29)

    def test_parse(self):
        # Barclays debit CDOL1
        dol_data = unformat_bytes('9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C 01 9F 37 04')
        dol = DOL.unmarshal(dol_data)

        # Parameters to GENERATE APPLICATION CRYPTOGRAM from barclays-pinsentry.c:
        data = unformat_bytes('''00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00 00 00 00
                                 01 01 01 00 00 00 00 00''')

        tlv = dol.parse(data)
        self.assertEqual(tlv[0x9A], [1, 1, 1])
