from collections import OrderedDict
from .data import (
    ELEMENT_FORMAT,
    render_element,
    read_tag,
    read_length,
    is_constructed,
    Tag,
)
from .data_elements import Parse, EPC_PRODUCT_ID
from ..util import decode_int, bit_set
import logging

log = logging.getLogger(__name__)


def parse_element(tag, value):
    if ELEMENT_FORMAT.get(tag) == Parse.DOL:
        value = DOL.unmarshal(value)
    elif ELEMENT_FORMAT.get(tag) == Parse.TAG_LIST:
        value = TagList.unmarshal(value)
    elif ELEMENT_FORMAT.get(tag) == Parse.ASRPD:
        value = ASRPD.unmarshal(value)
    elif ELEMENT_FORMAT.get(tag) == Parse.CVM_LIST:
        value = CVMList.unmarshal(value)
    elif ELEMENT_FORMAT.get(tag) == Parse.AUC:
        value = AUC.unmarshal(value)
    return value


class TLV(OrderedDict):
    """BER-TLV
    A serialisation format.

    Documented in EMV 4.3 Book 3 Annex B
    """

    @classmethod
    def unmarshal(cls, data):
        tlv = cls()
        i = 0

        if len(data) < 3:
            # A valid TLV record is at least three bytes, anything less is probably a bug.
            # I've seen some cards present this (with a TLV of simply [0x61]), so silently ignore.
            log.info("Invalid TLV - too short: %s", data)
            return data

        while i < len(data):
            tag, tag_len = read_tag(data[i:])
            i += tag_len
            if len(data) <= i:
                log.info("Invalid TLV - read beyond end of buffer at %s: %s", tag, data)
                return tlv

            length, length_len = read_length(data[i:])
            i += length_len

            value = data[i : i + length]

            if is_constructed(tag[0]):
                value = TLV.unmarshal(value)

            tag = Tag(tag)
            value = parse_element(tag, value)

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
            if (
                type(val) in (TLV, DOL)
                or type(val) is list
                and len(val) > 0
                and type(val[0]) in (TLV, DOL)
            ):
                out += str(val)
            else:
                out += render_element(key, val)
            vals.append(out)
        return "{" + (", ".join(vals)) + "}"


class ASRPD(dict):
    """Application Selection Registered Proprietary Data list.

    An almost-TLV structure used in the FCI Discretionary Data object.
    The tags here are fixed-length.

    https://www.emvco.com/wp-content/uploads/2017/05/BookB_Entry_Point_Specification_v2_6_20160809023257319.pdf
    """

    @classmethod
    def unmarshal(cls, data):
        asrpd = cls()

        i = 0

        while i < len(data):
            # 2 bytes Proprietary Data Identifier
            pdi = "%02i%02i" % tuple(data[i : i + 2])
            i += 2

            length = data[i]
            i += 1

            asrpd[pdi] = data[i : i + length]
            i += length

        return asrpd

    def __repr__(self):
        ret = "<ASRPD: "
        for pdi, value in self.items():
            if pdi == "0001":
                ret += "Electronic Product Identification: "
                ret += EPC_PRODUCT_ID.get(value[0], "Unknown")
        ret += ">"
        return ret


class DOL(OrderedDict):
    """Data Object List.
    This is sent by the card to the terminal to define a structure for
    future transactions, consisting of an ordered list of data elements and lengths.

    It's essentially a TLV object without the values.

    EMV 4.3 Book 3 section 5.4"""

    @classmethod
    def unmarshal(cls, data):
        """Construct a DOL object from the binary representation (as a list of bytes)"""
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
        """Total size of the resulting structure in bytes."""
        return sum(self.values())

    def unserialise(self, data):
        """Parse an input stream of bytes and return a TLV object."""
        if self.size() != len(data):
            raise Exception(
                "Incorrect input size (expecting %s bytes, got %s)"
                % (self.size(), len(data))
            )

        tlv = TLV()
        i = 0
        for tag, length in self.items():
            tlv[tag] = data[i : i + length]
            i += length

        return tlv

    def serialise(self, data):
        """Given a dictionary of tag -> value, write this data out
        according to the DOL. Missing data will be null.
        """
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


class TagList(list):
    """A list of tags."""

    @classmethod
    def unmarshal(cls, data):
        tag_list = cls()
        i = 0
        while i < len(data):
            tag, tag_len = read_tag(data[i:])
            i += tag_len
            tag_list.append(Tag(tag))
        return tag_list


class CVMRule(object):
    """EMV 4.3 book 3 appendix C3"""

    RULES = {
        # 0b00000000: "Fail CVM processing",
        0b00000001: "Plaintext PIN verification performed by ICC",
        0b00000010: "Enciphered PIN verified online",
        0b00000011: "Plaintext PIN verification performed by ICC and signature (paper)",
        0b00000100: "Enciphered PIN verification performed by ICC",
        0b00000101: "Enciphered PIN verification performed by ICC and signature (paper)",
        0b00011110: "Signature (paper)",
        0b00111111: "No CVM required",
    }

    CODES = {
        0: "Always",
        1: "If unattended cash",
        2: "If not unattended cash and not manual cash and not purchase with cashback",
        3: "If terminal supports the CVM",
        4: "If manual cash",
        5: "If purchase with cashback",
        6: "If transaction is in the application currency and is under X value",
        7: "If transaction is in the application currency and is over X value",
        8: "If transaction is in the application currency and is under Y value",
        9: "If transaction is in the application currency and is over Y value",
    }

    @classmethod
    def unmarshal(cls, b1, b2):
        rule = cls()
        rule.b1 = b1
        rule.b2 = b2
        return rule

    def rule_repr(self):
        for k, v in self.RULES.items():
            if (self.b1 & k) == k:
                return v
        return "Fail CVM processing"

    def code_repr(self):
        return self.CODES.get(self.b2)

    def fail_if_unsuccessful(self):
        return self.b1 & 0b01000000 == 0b01000000

    def __repr__(self):
        if self.fail_if_unsuccessful():
            fail = ". Else, fail verification."
        else:
            fail = ""

        return "%s, %s%s" % (self.code_repr(), self.rule_repr(), fail)


class CVMList(object):
    """CVM is a tiny language for the card to dictate when the terminal should fail the
        transaction or force it online.

        It doesn't seem to get much interesting use on many of the cards I've seen though.

    EMV 4.3 book 3 section 10.5"""

    def __init__(self):
        self.x = None
        self.y = None
        self.rules = []

    @classmethod
    def unmarshal(cls, data):
        cvm_list = cls()
        if len(data) < 10 or len(data) % 2 != 0:
            return cvm_list

        cvm_list.x = decode_int(data[0:4])
        cvm_list.y = decode_int(data[4:8])

        cvm_list.rules = []

        i = 8
        while i < len(data):
            cvm_list.rules.append(CVMRule.unmarshal(data[i], data[i + 1]))
            i += 2

        return cvm_list

    def __repr__(self):
        return "<CVM List x: %s, y: %s, rules: %s>" % (
            self.x,
            self.y,
            "; ".join([repr(r) for r in self.rules]),
        )


class AUC(object):

    B1_FIELDS = [
        "Valid for domestic cash transactions",
        "Valid for international cash transactions",
        "Valid for domestic goods",
        "Valid for international goods",
        "Valid for domestic services",
        "Valid for international services",
        "Valid at ATMs",
        "Valid at terminals other than ATMs",
    ]

    B2_FIELDS = ["Domestic cashback allowed", "International cashback allowed"]

    @classmethod
    def unmarshal(cls, data):
        auc = cls()
        if len(data) != 2:
            return auc

        auc.b1 = data[0]
        auc.b2 = data[1]
        return auc

    def get_uses(self):
        uses = []
        for i in range(0, len(self.B1_FIELDS)):
            if bit_set(self.b1, i):
                uses.append(self.B1_FIELDS[i])

        for i in range(0, len(self.B2_FIELDS)):
            if bit_set(self.b2, i):
                uses.append(self.B2_FIELDS[i])
        return uses

    def __repr__(self):
        return "<AUC: %s>" % ", ".join(self.get_uses())
