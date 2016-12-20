# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from emv import TransmissionProtocol
from emv.protocol.command import SelectCommand, ReadCommand, GetDataCommand


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
