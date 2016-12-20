# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from .dol import DOL
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
            elif tag in DOL_ELEMENTS:
                value = DOL.unmarshal(value)

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
                out += render_element(key, val)
            vals.append(out)
        return "{" + (", ".join(vals)) + "}"
