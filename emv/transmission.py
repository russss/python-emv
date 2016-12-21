# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import logging
from .protocol.response import RAPDU
from .util import format_bytes


class TransmissionProtocol(object):
    ''' Transport layer. Only currently supports T0 transport.

        Defined in: EMV 4.3 Book 1 section 9
        See also Annex A for examples.
    '''
    def __init__(self, connection):
        ''' Connection should be a pyscard connection. '''
        self.log = logging.getLogger(__name__)
        self.connection = connection
        self.connection.connect()
        assert connection.getProtocol() == connection.T0_protocol
        self.log.info("Connected to reader")

    def transmit(self, tx_data):
        ''' Send raw data to the card, and receive the reply.

            tx_data should be a list of bytes.

            Returns a tuple of (data, sw1, sw2) where sw1 and sw2
            are the protocol status bytes.
        '''
        self.log.debug("Tx: %s", format_bytes(tx_data))
        data, sw1, sw2 = self.connection.transmit(tx_data)
        self.log.debug("Rx: %s, SW1: %02x, SW2: %02x", format_bytes(data), sw1, sw2)
        return data, sw1, sw2

    def exchange(self, capdu):
        ''' Send a command to the card and return the response.

            Accepts a CAPDU object and returns a RAPDU.
        '''
        send_data = capdu.marshal()
        data, sw1, sw2 = self.transmit(send_data)

        if sw1 == 0x6C:
            # ICC asks to reduce data size requested
            send_data[4] = sw2
            data, sw1, sw2 = self.transmit(send_data)

        while sw1 == 0x61:
            # ICC has continuation data
            d, sw1, sw2 = self.transmit([0x00, 0xC0, 0x00, 0x00, sw2])
            data = data[:-2] + d

        res = RAPDU.unmarshal(data + [sw1, sw2])
        return res
