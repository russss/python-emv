# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from emv.util import unformat_bytes
from emv.protocol.command import SelectCommand
from emv.protocol.response import SuccessResponse
from emv.transmission import TransmissionProtocol


class MockConnection(object):
    T0_protocol = 1

    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    def connect(self):
        pass

    def getProtocol(self):
        return self.T0_protocol

    def transmit(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


class TestTransmission(TestCase):
    def test_simple(self):
        responses = [
            ([], 0x90, 0x00)
        ]

        conn = MockConnection(responses)
        tp = TransmissionProtocol(conn)
        res = tp.exchange(SelectCommand('test'))
        self.assertIs(type(res), SuccessResponse)

    def test_retry(self):
        r_data = unformat_bytes('''6F 1D 84 07 A0 00 00 00 03 80 02 A5 12 50 08 42 41
                                   52 43 4C 41 59 53 87 01 00 5F 2D 02 65 6E''')
        responses = [
            ([], 0x61, 0x1F),
            (r_data, 0x90, 0x00)
        ]

        conn = MockConnection(responses)
        tp = TransmissionProtocol(conn)
        res = tp.exchange(SelectCommand([0xA0, 0x00, 0x00, 0x00, 0x03, 0x80, 0x02]))
        self.assertIs(type(res), SuccessResponse)
