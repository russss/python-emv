# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from .response import RAPDU, SuccessResponse, WarningResponse, ErrorResponse


class TestRAPDU(TestCase):
    def test_unmarshal(self):
        pdu = RAPDU.unmarshal([0x90, 0x00])
        self.assertIs(type(pdu), SuccessResponse)

        pdu = RAPDU.unmarshal([0x63, 0xC2])
        self.assertIs(type(pdu), WarningResponse)

        pdu = RAPDU.unmarshal([0x6A, 0x81])
        self.assertIs(type(pdu), ErrorResponse)
