# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from emv import TransmissionProtocol
from emv.protocol.command import (SelectCommand, ReadCommand, GetDataCommand,
                                  GetProcessingOptions, VerifyCommand)


class Card(object):
    def __init__(self, connection):
        self.tp = TransmissionProtocol(connection)

    def list_applications(self):
        res = self.tp.exchange(SelectCommand('1PAY.SYS.DDF01'))
        sfi = res.data[0x6F][0xA5][0x88][0]
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
        data['atc'] = res.data[(0x9F, 0x36)]

        res = self.tp.exchange(GetDataCommand(GetDataCommand.LAST_ONLINE_ATC))
        data['last_online_atc'] = res.data[(0x9F, 0x13)]

        return data

    def get_processing_options(self):
        res = self.tp.exchange(GetProcessingOptions())
        if 0x80 in res.data:
            # Response template format 1
            return {'AIP': res.data[0x80][:2], 'AFL': res.data[0x80][2:]}
        elif 0x77 in res:
            # Response template format 2
            return {'AIP': res.data[0x77][0x82], 'AFL': res.data[0x77][0x94]}

    def get_application_data(self, afl):
        assert len(afl) % 4 == 0
        data = []
        for i in range(0, len(afl), 4):
            sfi = afl[i] >> 3
            start_rec = afl[i + 1]
            end_rec = afl[i + 2]
            # dar = afl[i + 3]
            for i in range(start_rec, end_rec + 1):
                res = self.tp.exchange(ReadCommand(start_rec, sfi))
                data.append(res.data)
        return data

    def verify_pin(self, pin):
        return self.tp.exchange(VerifyCommand(pin))
