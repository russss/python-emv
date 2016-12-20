# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from functools import total_ordering
from ..util import format_bytes

# EMV 4.3 Book 3 Annex A
DATA_ELEMENTS = {
    0x42: 'Issuer Identification Number',
    0x4F: 'Application Dedicated File (ADF) Name',
    0x50: 'Application Label',
    0x57: 'Track 2 Equivalent Data',
    0x5A: 'Application Primary Account Number (PAN)',
    (0x5F, 0x20): 'Cardholder Name',
    (0x5F, 0x24): 'Application Expiration Date',
    (0x5F, 0x25): 'Application Effective Date',
    (0x5F, 0x28): 'Issuer Country Code',
    (0x5F, 0x2D): 'Language Preference',
    (0x5F, 0x2A): 'Transaction Currency Code',
    (0x5F, 0x30): 'Service Code',
    (0x5F, 0x34): 'Application Primary Account Number (PAN) Sequence Number',
    0x61: 'Application Template',
    0x6F: 'FCI Template',
    0x70: 'Read Record Response Template',
    0x73: 'Directory Discretionary Template',
    0x77: 'Response Template Format 2',
    0x80: 'Response Template Format 1',
    0x8A: 'Authorisation Response Code',
    0x8C: 'Card Risk Management Data Object List 1 (CDOL1)',
    0x8D: 'Card Risk Management Data Object List 2 (CDOL2)',
    0x8E: 'Cardholder Verification Method (CVM) List',
    0x8F: 'Certification Authority Public Key Index',
    0x88: 'Short File Identifier',
    0x84: 'DF Name',
    0x87: 'Application Priority Indicator',
    0x95: 'Terminal Verification Results',
    0x97: 'Transaction Certificate Data Object List (TDOL)',
    0x9A: 'Transaction Date',
    0x9B: 'Transaction Status Information',
    0x9C: 'Transaction Type',
    0x9D: 'DDF Name',
    0xA5: 'FCI Proprietary Template',
    (0xBF, 0x0C): 'FCI Issuer Discretionary Data',
    (0x9F, 0x02): 'Amount, Authorised',
    (0x9F, 0x03): 'Amount, Other (Numeric)',
    (0x9F, 0x04): 'Amount, Other (Binary)',
    (0x9F, 0x05): 'Application Discretionary Data',
    (0x9F, 0x06): 'Application Identifier (AID) - terminal',
    (0x9F, 0x07): 'Application Usage Control',
    (0x9F, 0x08): 'Application Version Number',
    (0x9F, 0x09): 'Application Version Number',
    (0x9F, 0x0B): 'Cardholder Name Extended',
    (0x9F, 0x10): 'Issuer Application Data',
    (0x9F, 0x11): 'Issuer Code Table Index',
    (0x9F, 0x12): 'Application Preferred Name',
    (0x9F, 0x13): 'Last Online Application Transaction Counter (ATC) Register',
    (0x9F, 0x17): 'PIN Try Counter',
    (0x9F, 0x1A): 'Terminal Country Code',
    (0x9F, 0x21): 'Transaction Time',
    (0x9F, 0x26): 'Application Cryptogram',
    (0x9F, 0x27): 'Cryptogram Information Data',
    (0x9F, 0x36): 'Application Transaction Counter',
    (0x9F, 0x37): 'Unpredictable Number',
    (0x9F, 0x38): 'PDOL',
    (0x9F, 0x45): 'Data Authentication Code',
    (0x9F, 0x4E): 'Merchant Name and Location'
}

ASCII_ELEMENTS = [0x50, (0x9F, 0x0B)]
DOL_ELEMENTS = [0x8C, 0x8D, 0x97, (0x9F, 0x38)]


def is_two_byte(val):
    ''' A tag is at least two bytes long if the least significant
        5 bits of the first byte are set. '''
    return val & 0b00011111 == 0b00011111


def is_continuation(val):
    ''' Any subsequent byte is a continuation byte if the MSB is set. '''
    return val & 0b10000000 == 0b10000000


def is_constructed(val):
    ''' Check if a tag represents a "constructed" value, i.e. another TLV '''
    return val & 0b00100000 == 0b00100000


def read_tag(data):
    i = 0
    tag = [data[i]]
    if is_two_byte(data[i]):
        i += 1
        tag += [data[i]]
        i += 1
        while is_continuation(data[i]):
            tag += [data[i]]
            i += 1
    else:
        i += 1
    return tag, i


@total_ordering
class Tag(object):
    def __init__(self, value):
        self.value = value
        if len(self.value) == 1:
            self.value = self.value[0]

    @property
    def name(self):
        if type(self.value) == list:
            return DATA_ELEMENTS.get(tuple(self.value))
        else:
            return DATA_ELEMENTS.get(self.value)

    def __hash__(self):
        if type(self.value) == list:
            return hash(tuple(self.value))
        return hash(self.value)

    def __eq__(self, other):
        if type(other) == Tag:
            return (self.value == other.value)
        if type(other) in (tuple, list) and type(self.value) == list:
            return tuple(other) == tuple(self.value)

        return self.name == other or self.value == other

    def __lt__(self, other):
        if type(other) == Tag:
            return self.value < other.value

        return self.value < other

    def __repr__(self):
        if type(self.value) == list:
            val = format_bytes(self.value)
        else:
            val = '%02X' % self.value

        if self.name:
            return '(%s) %s' % (val, self.name)
        else:
            return val


def render_element(tag, value):
    if tag in ASCII_ELEMENTS:
        return '"' + ''.join(map(chr, value)) + '"'
    return format_bytes(value)
