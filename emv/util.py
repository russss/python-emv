# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import re


def hex_int(val):
    ''' Convert an integer into a decimal-encoded hex integer as bytes,
        which the EMV spec seems awfully keen on.

        >>> hex_int(123456)
        [0x12, 0x34, 0x56]
        >>> hex_int(65432)
        [0x06, 0x54, 0x32]
    '''
    s = str(val)
    if len(s) % 2 != 0:
        s = '0' + s
    return [int(s[i:i + 2], 16) for i in range(0, len(s), 2)]


def from_hex_int(val):
    ''' Convert hex digits to decimal.

        >>> from_hex_int([0x12, 0x34])
        1234
    '''
    return int(''.join(['%x' % i for i in val]))


def from_hex_date(val):
    return '%02x/%02x/%02x' % (val[0], val[1], val[2])


def decode_int(val):
    result = val[0]
    for i in val[1:]:
        result = result << 8
        result += i
    return result


def format_bytes(data):
    if type(data) == int:
        return "[%02X]" % data
    return "[" + ' '.join(['%02X' % i for i in data]) + "]"


def unformat_bytes(data):
    data = re.split('\s+', data)
    return [int(i, 16) for i in data]
