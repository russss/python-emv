# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from .transmission import TransmissionProtocol
from .protocol.structures import TLV
from .protocol.data import Tag
from .protocol.command import (SelectCommand, ReadCommand, GetDataCommand,
                               GetProcessingOptions, VerifyCommand)


def mkint16(data):
    return (data[0] << 8) + data[1]


class Card(object):
    ''' High-level card manipulation API '''
    def __init__(self, connection):
        self.tp = TransmissionProtocol(connection)

    def list_applications(self):
        res = self.tp.exchange(SelectCommand('1PAY.SYS.DDF01'))
        sfi = res.data[Tag.FCI][Tag.FCI_PROP][Tag.SFI][0]
        res = self.tp.exchange(ReadCommand(1, sfi))
        return res

    def select_application(self, app):
        res = self.tp.exchange(SelectCommand(app))
        return res

    def get_metadata(self):
        data = {}
        res = self.tp.exchange(GetDataCommand(GetDataCommand.PIN_TRY_COUNT))
        data['pin_retries'] = res.data[(0x9F, 0x17)][0]

        res = self.tp.exchange(GetDataCommand(GetDataCommand.ATC))
        data['atc'] = mkint16(res.data[(0x9F, 0x36)])

        res = self.tp.exchange(GetDataCommand(GetDataCommand.LAST_ONLINE_ATC))
        data['last_online_atc'] = mkint16(res.data[(0x9F, 0x13)])

        return data

    def get_processing_options(self):
        res = self.tp.exchange(GetProcessingOptions())
        if Tag.RMTF1 in res.data:
            # Response template format 1
            return {'AIP': res.data[Tag.RMTF1][:2], 'AFL': res.data[Tag.RMTF1][2:]}
        elif Tag.RMTF2 in res.data:
            # Response template format 2
            return {'AIP': res.data[Tag.RMTF2][0x82], 'AFL': res.data[Tag.RMTF2][0x94]}

    def get_application_data(self, afl):
        assert len(afl) % 4 == 0
        data = TLV()
        for i in range(0, len(afl), 4):
            sfi = afl[i] >> 3
            start_rec = afl[i + 1]
            end_rec = afl[i + 2]
            # dar = afl[i + 3]
            for i in range(start_rec, end_rec + 1):
                res = self.tp.exchange(ReadCommand(start_rec, sfi))
                data.update(res.data[Tag.RECORD])
        return data

    def verify_pin(self, pin):
        return self.tp.exchange(VerifyCommand(pin))
