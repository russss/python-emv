# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import re


def hex_int(val):
    ''' Convert an integer into a decimal-encoded hex integer as bytes,
        which the EMV spec seems awfully keen on.

        >>> hex_int(123456) == [0x12, 0x34, 0x56]
        >>> hex_int(65432) == [0x06, 0x54, 0x32]
    '''
    s = str(val)
    if len(s) % 2 != 0:
        s = '0' + s
    return [int(s[i:i + 2], 16) for i in range(0, len(s), 2)]


def format_bytes(data):
    return ("[" + ' '.join(['%02x' % i for i in data]) + "]").upper()


def unformat_bytes(data):
    data = re.split('\s+', data)
    return [int(i, 16) for i in data]
