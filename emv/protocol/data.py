# coding=utf-8
''' This module deals with tags - identifiers of pieces of data in the EMV protocol.
    Tags can be one or more bytes long, with a continuation system a bit like UTF-8.

    Tag coding is described in:
        EMV Version 4.3 Book 3 Annex B1
'''
from __future__ import division, absolute_import, print_function, unicode_literals
from functools import total_ordering
import pycountry
from .data_elements import ELEMENT_TABLE, SENSITIVE_TAGS, Parse
from ..util import format_bytes, from_hex_int, from_hex_date, decode_int

DATA_ELEMENTS = dict((tag, name) for tag, name, _, _ in ELEMENT_TABLE)
ELEMENT_FORMAT = dict((tag, parse) for tag, _, parse, _ in ELEMENT_TABLE if parse is not None)
ASCII_ELEMENTS = {tag for tag, _, parse, _ in ELEMENT_TABLE if parse == Parse.ASCII}
DOL_ELEMENTS = {tag for tag, _, parse, _ in ELEMENT_TABLE if parse == Parse.DOL}


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
    ''' Read a variable-length tag from a list of bytes, starting at the
        first byte. Returns the tag, plus the number of bytes read from
        the list.

        EMV 4.3 Book 3 Annex B1
    '''
    i = 0
    tag = [data[i]]
    if is_two_byte(data[i]):
        i += 1
        tag += [data[i]]
        i += 1
        while len(data) > i and is_continuation(data[i]):
            tag += [data[i]]
            i += 1
    else:
        i += 1
    return tag, i


@total_ordering
class Tag(object):
    ''' Represents a data tag. Provides ordering and pretty rendering.'''
    def __init__(self, value):
        if type(value) in (list, tuple) and len(value) == 1:
            self.value = value[0]
        elif type(value) == int:
            self.value = value
        else:
            self.value = list(value)

    @property
    def id(self):
        if type(self.value) == list:
            return tuple(self.value)
        else:
            return self.value

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


# Set element shortnames as static attributes on the Tag object.
for tag, _, _, shortname in ELEMENT_TABLE:
    if shortname is not None:
        setattr(Tag, shortname, tag)


def render_element(tag, value, redact=False):
    if type(tag) == Tag:
        tag = tag.id

    if redact and tag in SENSITIVE_TAGS:
        return '[REDACTED]'

    if type(value).__name__ in ('TLV', 'DOL', 'TagList'):
        return repr(value)
    parse = ELEMENT_FORMAT.get(tag)
    if parse is None:
        return format_bytes(value)
    if parse == Parse.ASCII:
        return '"' + ''.join(map(chr, value)) + '"'
    if parse == Parse.DEC:
        return str(from_hex_int(value))
    if parse == Parse.DATE:
        return from_hex_date(value)
    if parse == Parse.INT:
        return str(decode_int(value))
    if parse == Parse.COUNTRY:
        return pycountry.countries.get(numeric=str(from_hex_int(value))).alpha_2
    if parse == Parse.CURRENCY:
        return pycountry.currencies.get(numeric=str(from_hex_int(value))).alpha_3
    return format_bytes(value)
