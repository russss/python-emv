import pytest
from emv.protocol.response import RAPDU, SuccessResponse, WarningResponse, ErrorResponse


def test_unmarshal():
    pdu = RAPDU.unmarshal([0x90, 0x00])
    assert type(pdu) is SuccessResponse

    pdu = RAPDU.unmarshal([0x63, 0xC2])
    assert type(pdu) is WarningResponse

    with pytest.raises(ErrorResponse):
        RAPDU.unmarshal([0x6A, 0x81])
