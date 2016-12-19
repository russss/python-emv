# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals


def format_bytes(data):
    return ("[" + ' '.join(['%02x' % i for i in data]) + "]").upper()


def unformat_bytes(data):
    data = data.split(" ")
    return [int(i, 16) for i in data]
