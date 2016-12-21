# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from collections import OrderedDict
from .data import DOL_ELEMENTS, render_element, read_tag, is_constructed, Tag


class TLV(dict):
    ''' BER-TLV
        A serialisation format.

        Documented in EMV 4.3 Book 3 Annex B
    '''

    @classmethod
    def unmarshal(cls, data):
        tlv = cls()
        i = 0
        while i < len(data):
            tag, tag_len = read_tag(data[i:])
            i += tag_len
            length = data[i]
            i += 1
            value = data[i:i + length]

            if is_constructed(tag[0]):
                value = TLV.unmarshal(value)

            tag = Tag(tag)
            if tag in DOL_ELEMENTS:
                value = DOL.unmarshal(value)

            # If we have duplicate tags, make them into a list
            if tag in tlv:
                if type(tlv[tag]) is not list:
                    tlv[tag] = [tlv[tag]]
                tlv[tag].append(value)
            else:
                tlv[tag] = value
            i += length
        return tlv

    def __repr__(self):
        vals = []
        for key, val in self.items():
            out = "\n%s: " % str(key)
            if type(val) in (TLV, DOL) or \
               type(val) is list and len(val) > 0 and type(val[0]) in (TLV, DOL):
                out += str(val)
            else:
                out += render_element(key, val)
            vals.append(out)
        return "{" + (", ".join(vals)) + "}"


class DOL(OrderedDict):
    ''' Data Object List.
        This is sent by the card to the terminal to define a structure for
        future transactions, consisting of an ordered list of data elements and lengths.

        It's essentially a TLV object without the values.

        EMV 4.3 Book 3 section 5.4 '''

    @classmethod
    def unmarshal(cls, data):
        ''' Construct a DOL object from the binary representation (as a list of bytes) '''
        dol = cls()
        i = 0
        while i < len(data):
            tag, tag_len = read_tag(data[i:])
            i += tag_len
            length = data[i]
            i += 1
            dol[Tag(tag)] = length
        return dol

    def size(self):
        ''' Total size of the resulting structure in bytes. '''
        return sum(self.values())

    def unserialise(self, data):
        ''' Parse an input stream of bytes and return a TLV object. '''
        if self.size() != len(data):
            raise Exception("Incorrect input size (expecting %s bytes, got %s)" % (
                            self.size(), len(data)))

        tlv = TLV()
        i = 0
        for tag, length in self.items():
            tlv[tag] = data[i:i + length]
            i += length

        return tlv

    def serialise(self, data):
        ''' Given a dictionary of tag -> value, write this data out
            according to the DOL. Missing data will be null.
        '''
        output = []
        for tag, length in self.items():
            value = data.get(tag, [0x0] * length)
            if len(value) < length:
                # If the length is shorter than required, left-pad it.
                value = [0x0] * (length - len(value)) + value
            elif len(value) > length:
                raise Exception("Data for tag %s is too long" % tag)
            output += value

        assert len(output) == self.size()
        return output
