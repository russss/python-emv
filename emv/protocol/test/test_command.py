from __future__ import division, absolute_import, print_function, unicode_literals

# coding=utf-8
from unittest2 import TestCase
from emv.protocol.command import (
    CAPDU,
    SelectCommand,
    GenerateApplicationCryptogramCommand,
)
from emv.util import unformat_bytes


class TestCAPDU(TestCase):
    def test_unmarshal(self):
        pdu = CAPDU.unmarshal(unformat_bytes("00 A4 04 00 07 A0 00 00 00 03 80 02"))
        self.assertIs(type(pdu), SelectCommand)
        self.assertEqual(pdu.p1, 0x04)
        self.assertEqual(pdu.p2, 0x00)
        self.assertEqual(len(pdu.data), 0x07)
        self.assertEqual(pdu.le, None)

        pdu = CAPDU.unmarshal(
            unformat_bytes(
                """80 AE 80 00 1D 00 00 00 00 00 00 00 00 00 00 00 00
                              00 00 80 00 00 00 00 00 00 01 01 01 00 00 00 00 00"""
            )
        )
        self.assertIs(type(pdu), GenerateApplicationCryptogramCommand)
        self.assertEqual(pdu.p1, 0x80)
        self.assertEqual(pdu.p2, 0x00)
        self.assertEqual(len(pdu.data), 0x1D)
        self.assertEqual(pdu.le, None)
