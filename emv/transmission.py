# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from .protocol.response import RAPDU


class TransmissionProtocol(object):
    ''' Transport layer.

        Defined in: EMV 4.3 Book 1 section 9
        See also Annex A for examples.
    '''
    def __init__(self, connection):
        self.connection = connection

    def exchange(self, capdu):
        ''' Send a command to the card and return the response.

            Only currently supports T0 transport.
        '''
        send_data = capdu.marshal()
        data = self.connection.transmit(send_data)
        assert len(data) > 1

        if data[-2] == 0x6C:
            # ICC asks to reduce data size requested
            send_data[4] = data[-1]
            data = self.connection.transmit(send_data)

        while data[-2] == 0x61:
            # ICC has continuation data
            data = data[:-2] + self.connection.transmit([0x00, 0xC0, 0x00, 0x00, data[:-1]])

        return RAPDU.unmarshal(data)
