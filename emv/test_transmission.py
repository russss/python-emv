# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from unittest2 import TestCase
from .protocol.command import SelectCommand
from .protocol.response import SuccessResponse
from .transmission import TransmissionProtocol


class MockConnection(object):
    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    def transmit(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


class TestTransmission(TestCase):
    def test_simple(self):
        responses = [
            [0x90, 0x00]
        ]

        conn = MockConnection(responses)
        tp = TransmissionProtocol(conn)
        res = tp.exchange(SelectCommand('test'))
        self.assertIs(type(res), SuccessResponse)
