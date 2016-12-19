# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from ..util import format_bytes
import six


def assert_valid_byte(val):
    assert type(val) == int
    assert val < 0xFF
    assert val >= 0x00


class CAPDU(object):
    ''' Command APDU.

        Defined in: EMV 4.3 Book 1 sections:
            - 9.4.1
            - 11.1
    '''

    # Map the class name of the command to the CLA,INS bytes.
    # This is derived from EMV 4.3 Book 3 section 6.3.2.
    COMMANDS = {
        'SelectCommand': [0x00, 0xA4],
        'VerifyCommand': [0x00, 0x20],
        'ReadCommand': [0x00, 0xB2],
        'GenerateApplicationCryptogramCommand': [0x80, 0xAE],
        'GetProcessingOptions': [0x80, 0xA8]
    }

    def marshal(self):
        cla, ins = self.COMMANDS.get(self.__class__.__name__)

        for val in [cla, ins, self.p1, self.p2]:
            assert_valid_byte(val)

        # Mandatory header:
        cmd = [cla, ins, self.p1, self.p2]

        # Conditional body:
        if self.data is not None:
            cmd += [len(self.data)]  # Lc
            cmd += self.data

        # Bytes expected:
        if self.le is not None:
            cmd += [self.le]  # Le
        return cmd

    @classmethod
    def get_class(cls, pdu_bytes):
        for clsname, b in cls.COMMANDS.items():
            if pdu_bytes == b:
                return globals()[clsname]
        return None

    @classmethod
    def unmarshal(cls, data):
        pcls = cls.get_class(data[:2])
        obj = object.__new__(pcls)
        obj.p1 = data[2]
        obj.p2 = data[3]
        if len(data) > 5:
            obj.lc = data[4]
            obj.data = data[5:obj.lc + 5]
        if len(data) > obj.lc + 5:
            obj.le = data[-1]
        else:
            obj.le = None
        return obj

    def __repr__(self):
        return '<Command[%s] P1: %02x, P2: %02x, data: %s, Le: %02x>' % (
            self.name, self.p1, self.p2, format_bytes(self.data), self.le or 0)


class SelectCommand(CAPDU):
    ''' Select an application or file on the card.

        Defined in: EMV 4.3 Book 1 section 11.3
    '''
    name = 'Select'

    def __init__(self, file_name):
        if isinstance(file_name, six.string_types):
            self.data = [ord(c) for c in file_name]
        else:
            self.data = file_name

        self.p1 = 0x04  # Select by name
        self.p2 = 0x00  # First or only occurrence

        self.le = 0x00

    def __repr__(self):
        data = ' '.join(['%02x' % i for i in self.data])
        return '<Command[%s] P1: %02x, P2: %02x, File name: %s, Le: %02x>' % (
            self.name, self.p1, self.p2, data.upper(), self.le or 0)


class ReadCommand(CAPDU):
    ''' Read a record from an application or file.

        Defined in: EMV 4.3 Book 1 section 11.2
    '''
    name = 'Read'

    P2_RECORD_NUMBER = 0x04  # P1 is a record number

    def __init__(self, record_number=None, sfi=None):
        assert record_number is not None or sfi is not None

        if record_number is not None:
            assert type(record_number) == int
            self.p1 = record_number
            self.p2 = self.P2_RECORD_NUMBER
        else:
            assert False  # TODO: read by SFI

        self.le = 0x00


class VerifyCommand(CAPDU):
    ''' Verify the PIN.

        Defined in: EMV 4.3 Book 3 section 6.5.12
    '''
    name = 'Verify'

    PIN_PLAINTEXT = 0b10000000
    PIN_ENCIPHERED = 0b10001000

    def __init__(self, pin):
        assert 4 <= len(str(pin)) <= 12

        self.p1 = 0x00
        self.p2 = self.PIN_PLAINTEXT

        data = b'2%x%s' % (len(str(pin)), pin)
        while len(data) < 16:
            data += 'f'
        self.data = [ord(i) for i in data.decode('hex')]

        self.le = 0x00


class GenerateApplicationCryptogramCommand(CAPDU):
    ''' Defined in: EMV 4.3 Book 3 section 6.5.5 '''
    name = 'Generate Application Cryptogram'

    # Table 12
    AAC = 0b00000000
    TC = 0b01000000
    ARQC = 0b10000000
    CDA_SIG = 0b00010000

    def __init__(self, crypto_type, data, cda_sig=False):

        self.p1 = crypto_type
        if cda_sig:
            self.p1 |= self.CDA_SIG

        self.data = data

        self.p2 = 0x00
        self.le = 0x00


class GetProcessingOptions(CAPDU):
    ''' Defined in: EMV 4.3 Book 3 section 6.5.8 '''
    name = 'Get Processing Opts'

    def __init__(self):
        self.p1 = 0x00
        self.p2 = 0x00
        self.le = 0x00
