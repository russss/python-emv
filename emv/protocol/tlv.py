# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from functools import total_ordering
from ..util import format_bytes
from .data import DATA_ELEMENTS, ASCII_ELEMENTS
# EMV 4.3 Book 3 Annex B


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
        if type(other) in (tuple, list):
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
            elif key in ASCII_ELEMENTS:
                out += '"' + ''.join(map(chr, val)) + '"'
            else:
                out += format_bytes(val)
            vals.append(out)
        return "{" + (", ".join(vals)) + "}"
