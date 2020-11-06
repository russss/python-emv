import pytest
from emv.util import unformat_bytes
from emv.test.fixtures import APP_DATA
from emv.protocol.data import Tag
from emv.protocol.structures import TLV, DOL, TagList, read_tag, CVMList


def test_tlv():
    data = unformat_bytes(
        """6F 1D 84 07 A0 00 00 00 03 80 02 A5 12 50 08 42 41 52 43 4C
                             41 59 53 87 01 00 5F 2D 02 65 6E"""
    )
    tlv = TLV.unmarshal(data)
    assert 0x50 in tlv[Tag.FCI][Tag.FCI_PROP]

    data = unformat_bytes(
        """77 1E 9F 27 01 80 9F 36 02 00 05 9F 26 08 6E CF 93 47 C1 A9
                             24 71 9F 10 07 06 0B 0A 03 A4 90 00"""
    )
    tlv = TLV.unmarshal(data)
    assert Tag.RMTF2 in tlv
    assert (0x9F, 0x26) in tlv[Tag.RMTF2]
    assert tlv[Tag.RMTF2][(0x9F, 0x26)] == unformat_bytes("6E CF 93 47 C1 A9 24 71")

    data = unformat_bytes("9F 17 01 03")
    tlv = TLV.unmarshal(data)
    assert tlv[(0x9F, 0x17)][0] == 3

    data = unformat_bytes("DF DF 39 01 07")
    tlv = TLV.unmarshal(data)
    assert tlv[(0xDF, 0xDF, 0x39)][0] == 7


def test_length_parsing():
    data = unformat_bytes("42 01 03")
    tlv = TLV.unmarshal(data)
    assert tlv[0x42][0] == 3

    data = unformat_bytes("42 81 01 07")
    tlv = TLV.unmarshal(data)
    assert tlv[0x42][0] == 7

    data = unformat_bytes("42 82 00 01 07")
    tlv = TLV.unmarshal(data)
    assert tlv[0x42][0] == 7

    data = unformat_bytes("42 83 00 00 01 07")
    tlv = TLV.unmarshal(data)
    assert tlv[0x42][0] == 7


def test_duplicate_tags():
    # An ADF entry with a number of records:
    data = unformat_bytes(
        """70 4A 61 16 4F 07 A0 00 00 00 29 10 10 50 08 4C 49 4E 4B 20
                                        41 54 4D 87 01 01
                                   61 18 4F 07 A0 00 00 00 03 10 10 50 0A 56 49 53 41 20
                                        44 45 42 49 54 87 01 02
                                   61 16 4F 07 A0 00 00 00 03 80 02 50 08 42 41 52 43 4C
                                        41 59 53 87 01 00"""
    )
    tlv = TLV.unmarshal(data)
    assert Tag.RECORD in tlv
    assert Tag.APP in tlv[Tag.RECORD]

    # We expect this to be a list of TLV objects
    assert type(tlv[Tag.RECORD][Tag.APP]) is list
    assert len(tlv[Tag.RECORD][Tag.APP]) == 3
    repr(tlv)


def test_nested_dol():
    tlv = TLV.unmarshal(APP_DATA)
    repr(tlv)
    assert Tag.RECORD in tlv
    assert type(tlv[Tag.RECORD][Tag.CDOL1]) is DOL


def test_invalid_tlv():
    # An actual bit of data found on a card. 0x61 indicates that it's TLV format but
    # no following bytes make it invalid.
    data = unformat_bytes("61")
    assert TLV.unmarshal(data) == [0x61]


# Barclays debit CDOL1
dol_data = unformat_bytes(
    "9F 02 06 9F 03 06 9F 1A 02 95 05 5F 2A 02 9A 03 9C 01 9F 37 04"
)


def test_dol():
    dol = DOL.unmarshal(dol_data)
    assert 0x9A in dol
    assert dol[0x9A] == 3
    assert (0x9F, 0x37) in dol
    assert dol[(0x9F, 0x37)] == 4
    assert dol.size() == 29


def test_serialise():
    dol = DOL.unmarshal(dol_data)

    # Parameters to GENERATE APPLICATION CRYPTOGRAM from barclays-pinsentry.c:
    data = unformat_bytes(
        """00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00 00 00 00
                             01 01 01 00 00 00 00 00"""
    )

    tlv = dol.unserialise(data)
    assert tlv[0x9A] == [1, 1, 1]

    # Re-serialise by round trip
    assert dol.serialise(tlv) == data

    # Serialise with partial data
    source = {
        Tag(0x9A): [0x01, 0x01, 0x01],
        Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00],
    }

    serialised = dol.serialise(source)
    assert serialised == data


def test_serialise_long_data():
    dol = DOL.unmarshal(dol_data)

    # First tag is too long for the DOL
    source = {
        Tag(0x9A): [0x01, 0x01, 0x01, 0x02],
        Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00],
    }

    with pytest.raises(Exception):
        dol.serialise(source)


def test_unserialise():
    dol = DOL.unmarshal(dol_data)

    # Incorrect length data
    data = unformat_bytes(
        """00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00 00 00 00
                             00 00 00"""
    )

    with pytest.raises(Exception):
        dol.unserialise(data)


def test_read_tag():
    assert read_tag(unformat_bytes("82"))[0] == [0x82]
    assert read_tag(unformat_bytes("9F 42"))[0] == [0x9F, 0x42]


def test_taglist():
    data = unformat_bytes("82")
    taglist = TagList.unmarshal(data)
    assert len(taglist) == 1

    data = unformat_bytes("82 9F 42")
    taglist = TagList.unmarshal(data)
    assert len(taglist) == 2


def test_cvmlist():
    data = unformat_bytes("00 00 00 00 00 00 00 00 41 03 1E 03 02 03 1F 03")
    print(CVMList.unmarshal(data))
