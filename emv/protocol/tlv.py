# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from ..util import format_bytes
# EMV 4.3 Book 3 Annex B

NAMES = {
    0x50: 'Application Label',
    0x6F: 'FCI Template',
    0x73: 'Directory Discretionary Template',
    0x77: 'Response Format 2',
    0x80: 'Response Format 1',
    0x84: 'DF Name',
    0x87: 'Application Priority Indicator',
    0x9A: 'Transaction Date',
    0x9D: 'DDF Name',
    0xA5: 'FCI Proprietary Template',
    (0x5F, 0x2D): 'Language Preference',
    (0x5F, 0x2A): 'Transaction Currency Code',
    (0xBF, 0x0C): 'FCI Issuer Discretionary Data',
    (0x9F, 0x02): 'Amount, Authorised',
    (0x9F, 0x10): 'Issuer Application Data',
    (0x9F, 0x11): 'Issuer Code Table Index',
    (0x9F, 0x12): 'Application Preferred Name',
    (0x9F, 0x21): 'Transaction Time',
    (0x9F, 0x26): 'Application Cryptogram',
    (0x9F, 0x27): 'Cryptogram Information Data',
    (0x9F, 0x36): 'Application Transaction Counter',
    (0x9F, 0x38): 'PDOL',
    (0x9F, 0x45): 'Data Authentication Code',
    (0x9F, 0x4E): 'Merchant Name and Location',
}


def is_two_byte(val):
    ''' A tag is at least two bytes long if the least significant
        5 bits of the first byte are set. '''
    return val & 0b00011111 == 0b00011111


def is_continuation(val):
    ''' Any subsequent byte is a continuation byte if the MSB is set. '''
    return val & 0b10000000 == 0b10000000


def is_constructed(val):
    return val & 0b00100000 == 0b00100000


class Tag(object):
    def __init__(self, value):
        self.value = value
        if len(self.value) == 1:
            self.value = self.value[0]

    def __repr__(self):
        if type(self.value) == list:
            if tuple(self.value) in NAMES:
                return NAMES[tuple(self.value)]
            else:
                return format_bytes(self.value)
        else:
            if self.value in NAMES:
                return NAMES[self.value]
            else:
                return '%02X' % self.value


class TLV(dict):
    @classmethod
    def unmarshal(cls, data):
        tlv = cls()
        i = 0
        while i < len(data):
            tag = [data[i]]
            if is_two_byte(data[i]):
                i += 1
                tag += [data[i]]
                i += 1
                while is_continuation(data[i]):
                    tag += [data[i]]
                    i += 1
                i += 1
            else:
                i += 1
            length = data[i]
            i += 1
            value = data[i:i + length]
            if is_constructed(tag[0]):
                value = TLV.unmarshal(value)
            tlv[Tag(tag)] = value
            i += length
        return tlv

    def __repr__(self):
        vals = []
        for key, val in self.items():
            out = "%s: " % key
            if type(val) == TLV:
                out += "\n\t" + str(val) + "\n"
            else:
                out += format_bytes(val)
            vals.append(out)
        return "{" + (", ".join(vals)) + "}"
