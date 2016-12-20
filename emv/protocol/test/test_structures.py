# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from emv.util import unformat_bytes
from emv.fixtures import APP_DATA
from emv.protocol.data import Tag
from emv.protocol.structures import TLV, DOL


class TestTLV(TestCase):
    def test_tlv(self):
        data = unformat_bytes('''6F 1D 84 07 A0 00 00 00 03 80 02 A5 12 50 08 42 41 52 43 4C
                                 41 59 53 87 01 00 5F 2D 02 65 6E''')
        tlv = TLV.unmarshal(data)
        self.assertIn(0x50, tlv[Tag.FCI][Tag.FCI_PROP])

        data = unformat_bytes('''77 1E 9F 27 01 80 9F 36 02 00 05 9F 26 08 6E CF 93 47 C1 A9
                                 24 71 9F 10 07 06 0B 0A 03 A4 90 00''')
        tlv = TLV.unmarshal(data)
        self.assertIn(Tag.RMTF2, tlv)
        self.assertIn((0x9F, 0x26), tlv[Tag.RMTF2])
        self.assertEqual(tlv[Tag.RMTF2][(0x9F, 0x26)],
                         unformat_bytes('6E CF 93 47 C1 A9 24 71'))

        data = unformat_bytes('9F 17 01 03')
        tlv = TLV.unmarshal(data)
        self.assertEqual(tlv[(0x9F, 0x17)][0], 3)

    def test_nested_dol(self):
        tlv = TLV.unmarshal(APP_DATA)
        repr(tlv)
        self.assertIn(Tag.RECORD, tlv)
        self.assertIs(type(tlv[Tag.RECORD][Tag.CDOL1]), DOL)


class TestDOL(TestCase):
    def test_dol(self):
        data = unformat_bytes('9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C 01 9F 37 04')
        dol = DOL.unmarshal(data)
        self.assertIn(0x9A, dol)
        self.assertEqual(dol[0x9A], 3)
        self.assertIn((0x9F, 0x37), dol)
        self.assertEqual(dol[(0x9F, 0x37)], 4)
        self.assertEqual(dol.size(), 29)

    def test_serialise(self):
        # Barclays debit CDOL1
        dol_data = unformat_bytes('9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C 01 9F 37 04')
        dol = DOL.unmarshal(dol_data)

        # Parameters to GENERATE APPLICATION CRYPTOGRAM from barclays-pinsentry.c:
        data = unformat_bytes('''00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00 00 00 00
                                 01 01 01 00 00 00 00 00''')

        tlv = dol.unserialise(data)
        self.assertEqual(tlv[0x9A], [1, 1, 1])

        # Re-serialise by round trip
        self.assertEqual(dol.serialise(tlv), data)

        # Serialise with partial data
        source = {Tag(0x9A): [0x01, 0x01, 0x01],
                  Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00]}

        serialised = dol.serialise(source)
        self.assertEqual(serialised, data)
