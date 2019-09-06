# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from emv.util import unformat_bytes
from emv.test.fixtures import APP_DATA
from emv.protocol.data import Tag
from emv.protocol.structures import TLV, DOL, TagList, read_tag, CVMList


class TestTLV(TestCase):
    def test_tlv(self):
        data = unformat_bytes(
            """6F 1D 84 07 A0 00 00 00 03 80 02 A5 12 50 08 42 41 52 43 4C
                                 41 59 53 87 01 00 5F 2D 02 65 6E"""
        )
        tlv = TLV.unmarshal(data)
        self.assertIn(0x50, tlv[Tag.FCI][Tag.FCI_PROP])

        data = unformat_bytes(
            """77 1E 9F 27 01 80 9F 36 02 00 05 9F 26 08 6E CF 93 47 C1 A9
                                 24 71 9F 10 07 06 0B 0A 03 A4 90 00"""
        )
        tlv = TLV.unmarshal(data)
        self.assertIn(Tag.RMTF2, tlv)
        self.assertIn((0x9F, 0x26), tlv[Tag.RMTF2])
        self.assertEqual(
            tlv[Tag.RMTF2][(0x9F, 0x26)], unformat_bytes("6E CF 93 47 C1 A9 24 71")
        )

        data = unformat_bytes("9F 17 01 03")
        tlv = TLV.unmarshal(data)
        self.assertEqual(tlv[(0x9F, 0x17)][0], 3)

    def test_length_parsing(self):
        data = unformat_bytes("42 01 03")
        tlv = TLV.unmarshal(data)
        self.assertEqual(tlv[0x42][0], 3)

        data = unformat_bytes("42 81 01 07")
        tlv = TLV.unmarshal(data)
        self.assertEqual(tlv[0x42][0], 7)

        data = unformat_bytes("42 82 00 01 07")
        tlv = TLV.unmarshal(data)
        self.assertEqual(tlv[0x42][0], 7)

        data = unformat_bytes("42 83 00 00 01 07")
        tlv = TLV.unmarshal(data)
        self.assertEqual(tlv[0x42][0], 7)

    def test_duplicate_tags(self):
        # An ADF entry with a number of records:
        data = unformat_bytes(
            """70 4A 61 16 4F 07 A0 00 00 00 29 10 10 50 08 4C 49 4E 4B 20
                                            41 54 4D 87 01 01
                                       61 18 4F 07 A0 00 00 00 03 10 10 50 0A 56 49 53 41 20
                                            44 45 42 49 54 87 01 02
                                       61 16 4F 07 A0 00 00 00 03 80 02 50 08 42 41 52 43 4C
                                            41 59 53 87 01 00"""
        )
        tlv = TLV.unmarshal(data)
        self.assertIn(Tag.RECORD, tlv)
        self.assertIn(Tag.APP, tlv[Tag.RECORD])

        # We expect this to be a list of TLV objects
        self.assertIs(list, type(tlv[Tag.RECORD][Tag.APP]))
        self.assertEqual(len(tlv[Tag.RECORD][Tag.APP]), 3)
        repr(tlv)

    def test_nested_dol(self):
        tlv = TLV.unmarshal(APP_DATA)
        repr(tlv)
        self.assertIn(Tag.RECORD, tlv)
        self.assertIs(type(tlv[Tag.RECORD][Tag.CDOL1]), DOL)

    def test_invalid_tlv(self):
        # An actual bit of data found on a card. 0x61 indicates that it's TLV format but
        # no following bytes make it invalid.
        data = unformat_bytes("61")
        self.assertEqual(TLV.unmarshal(data), [0x61])


class TestDOL(TestCase):
    # Barclays debit CDOL1
    dol_data = unformat_bytes(
        "9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C 01 9F 37 04"
    )

    def test_dol(self):
        dol = DOL.unmarshal(self.dol_data)
        self.assertIn(0x9A, dol)
        self.assertEqual(dol[0x9A], 3)
        self.assertIn((0x9F, 0x37), dol)
        self.assertEqual(dol[(0x9F, 0x37)], 4)
        self.assertEqual(dol.size(), 29)

    def test_serialise(self):
        dol = DOL.unmarshal(self.dol_data)

        # Parameters to GENERATE APPLICATION CRYPTOGRAM from barclays-pinsentry.c:
        data = unformat_bytes(
            """00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00 00 00 00
                                 01 01 01 00 00 00 00 00"""
        )

        tlv = dol.unserialise(data)
        self.assertEqual(tlv[0x9A], [1, 1, 1])

        # Re-serialise by round trip
        self.assertEqual(dol.serialise(tlv), data)

        # Serialise with partial data
        source = {
            Tag(0x9A): [0x01, 0x01, 0x01],
            Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00],
        }

        serialised = dol.serialise(source)
        self.assertEqual(serialised, data)

    def test_serialise_long_data(self):
        dol = DOL.unmarshal(self.dol_data)

        # First tag is too long for the DOL
        source = {
            Tag(0x9A): [0x01, 0x01, 0x01, 0x02],
            Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00],
        }

        with self.assertRaises(Exception):
            dol.serialise(source)

    def test_unserialise(self):
        dol = DOL.unmarshal(self.dol_data)

        # Incorrect length data
        data = unformat_bytes(
            """00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00 00 00 00
                                 00 00 00"""
        )

        with self.assertRaises(Exception):
            dol.unserialise(data)


class TestTagList(TestCase):
    def test_read_tag(self):
        read_tag(unformat_bytes("82")) == [0x82]
        read_tag(unformat_bytes("9F 42")) == [0x9F, 0x42]

    def test_taglist(self):
        data = unformat_bytes("82")
        taglist = TagList.unmarshal(data)
        self.assertEqual(len(taglist), 1)

        data = unformat_bytes("82 9F 42")
        taglist = TagList.unmarshal(data)
        self.assertEqual(len(taglist), 2)


class TestCVMList(TestCase):
    def test_main(self):
        data = unformat_bytes("00 00 00 00 00 00 00 00 41 03 1E 03 02 03 1F 03")
        print(CVMList.unmarshal(data))
