from emv.protocol.response import RAPDU
from emv.protocol.structures import TLV
from emv.util import unformat_bytes
from emv.cap import get_cap_value, get_arqc_req

from emv.test.fixtures import APP_DATA


# Issuer Proprietary Bitmap used in Barclays cards
BARCLAYS_IPB = unformat_bytes("80 00 FF 00 00 00 00 00 01 FF FF 00 00 00 00 00 00 00")


def test_arqc_req():
    # Comparing with a valid test request from barclays_pinsentry.c
    req = get_arqc_req(TLV.unmarshal(APP_DATA)[0x70])
    data = unformat_bytes(
        """80 AE 80 00 1D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00
                             00 00 00 00 00 01 01 01 00 00 00 00 00 00"""
    )
    assert req.marshal() == data


def test_arqc_req_payment():
    # Payment of £1234.56, account number of 78901234
    req = get_arqc_req(TLV.unmarshal(APP_DATA)[0x70], value=1234.56, challenge=78901234)
    data = unformat_bytes(
        """80 AE 80 00 1D 00 00 00 12 34 56 00 00 00 00 00 00 00 00 80 00
                             00 00 00 00 00 01 01 01 00 78 90 12 34 00"""
    )
    assert req.marshal() == data

    # Payment of £15.00, account number of 78901234
    req = get_arqc_req(TLV.unmarshal(APP_DATA)[0x70], value=15.00, challenge=78901234)
    data = unformat_bytes(
        """80 AE 80 00 1D 00 00 00 00 15 00 00 00 00 00 00 00 00 00 80 00
                             00 00 00 00 00 01 01 01 00 78 90 12 34 00"""
    )
    assert req.marshal() == data


def test_arqc_req_challenge():
    # Challenge of 78901234
    req = get_arqc_req(TLV.unmarshal(APP_DATA)[0x70], challenge=78901234)
    data = unformat_bytes(
        """80 AE 80 00 1D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00
                             00 00 00 00 00 01 01 01 00 78 90 12 34 00"""
    )
    assert req.marshal() == data


def test_real_response_rmtf1():
    # Real response from barclays-pinsentry.c, with its calculated response.
    # This was an older card which used the RMTF1 response format
    data = unformat_bytes(
        "80 12 80 09 5F 0F 9D 37 98 E9 3F 12 9A 06 0A 0A 03 A4 90 00 90 00"
    )
    res = RAPDU.unmarshal(data)
    assert get_cap_value(res, ipb=BARCLAYS_IPB, psn=None) == 46076570


def test_real_response_rmtf2():
    # Real response from a new (2018) Barclays card using RMTF2 response format.
    data = unformat_bytes(
        """77 1E 9F 27 01 80 9F 36 02 00 16 9F 26 08 29 9C C8 F1 0B 9B C8
                             30 9F 10 07 06 0B 0A 03 A4 90 00"""
    )
    res = RAPDU.unmarshal(data)
    assert get_cap_value(res, ipb=BARCLAYS_IPB, psn=None) == 36554800
