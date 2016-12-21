# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from .transmission import TransmissionProtocol
from .protocol.structures import TLV
from .protocol.data import Tag
from .protocol.response import WarningResponse
from .protocol.command import (SelectCommand, ReadCommand, GetDataCommand,
                               GetProcessingOptions, VerifyCommand)
from .exc import InvalidPINException
from .util import decode_int
from .cap import get_arqc_req, get_cap_value


class Card(object):
    ''' High-level card manipulation API '''
    def __init__(self, connection):
        self.tp = TransmissionProtocol(connection)

    def get_mf(self):
        ''' Get the master file (MF). '''
        return self.tp.exchange(SelectCommand(file_identifier=[0x3F, 0x00]))

    def list_applications(self):
        res = self.tp.exchange(SelectCommand('1PAY.SYS.DDF01'))
        sfi = res.data[Tag.FCI][Tag.FCI_PROP][Tag.SFI][0]
        res = self.tp.exchange(ReadCommand(1, sfi))
        return res.data[Tag.RECORD][Tag.APP]

    def read_record(self, record_number, sfi=None):
        return self.tp.exchange(ReadCommand(record_number, sfi))

    def select_application(self, app):
        res = self.tp.exchange(SelectCommand(app))
        return res

    def get_metadata(self):
        data = {}
        res = self.tp.exchange(GetDataCommand(GetDataCommand.PIN_TRY_COUNT))
        data['pin_retries'] = res.data[(0x9F, 0x17)][0]

        res = self.tp.exchange(GetDataCommand(GetDataCommand.ATC))
        data['atc'] = decode_int(res.data[(0x9F, 0x36)])

        res = self.tp.exchange(GetDataCommand(GetDataCommand.LAST_ONLINE_ATC))
        data['last_online_atc'] = decode_int(res.data[(0x9F, 0x13)])

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
        ''' Verify the PIN, raising an exception if it fails.'''
        res = self.tp.exchange(VerifyCommand(pin))
        if type(res) == WarningResponse:
            raise InvalidPINException(str(res))

        return res

    def generate_cap_value(self, pin, challenge=None, value=None):
        ''' Perform a transaction to generate the EMV CAP (Pinsentry) value. '''
        apps = self.list_applications()

        # We're selecting the last app on the card here, which on Barclays
        # cards seems to always be the Barclays one.
        #
        # It would be good to work out what logic to use to work out
        # which app is responsible for CAP.
        self.select_application(apps[-1][Tag.ADF_NAME])

        # Get Processing Options starts the transaction on the card and
        # increments the transaction counter.
        opts = self.get_processing_options()

        # Fetch the application data referenced in the processing options.
        # This includes the CDOL data structure which dictates the format
        # of the data passed to the Get Application Cryptogram function.
        app_data = self.get_application_data(opts['AFL'])

        self.verify_pin(pin)

        resp = self.tp.exchange(get_arqc_req(app_data, challenge=challenge, value=value))
        return get_cap_value(resp)
