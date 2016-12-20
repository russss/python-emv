# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from emv.protocol.response import RAPDU
from emv.protocol.structures import TLV
from emv.fixtures import APP_DATA
from emv.util import unformat_bytes
from emv.cap import get_cap_value, get_arqc_req


class TestCAP(TestCase):

    def test_arqc_req(self):
        # Comparing with a valid test request from barclays_pinsentry.c
        req = get_arqc_req(TLV.unmarshal(APP_DATA)[0x70])
        data = unformat_bytes('''80 AE 80 00 1D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00
                                 00 00 00 00 00 01 01 01 00 00 00 00 00 00''')
        self.assertEqual(req.marshal(), data)

    def test_pinsentry_equivalence(self):
        # Real response from barclays-pinsentry.c, with its calculated response
        data = unformat_bytes('80 12 80 09 5F 0F 9D 37 98 E9 3F 12 9A 06 0A 0A 03 A4 90 00 90 00')
        res = RAPDU.unmarshal(data)
        self.assertEqual(get_cap_value(res), 46076570)
