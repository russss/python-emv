# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from collections import OrderedDict
from .data import read_tag, Tag


class DOL(OrderedDict):
    ''' Data Object List.
        This is sent by the card to the terminal to define a structure for
        future transactions, consisting of an ordered list of data elements and lengths.

        It's essentially a TLV object without the values.

        EMV 4.3 Book 3 section 5.4 '''
    @classmethod
    def unmarshal(cls, data):
        dol = cls()
        i = 0
        while i < len(data):
            tag, tag_len = read_tag(data[i:])
            i += tag_len
            length = data[i]
            i += 1
            dol[Tag(tag)] = length
        return dol
