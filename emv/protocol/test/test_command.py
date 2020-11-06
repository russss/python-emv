from emv.protocol.command import (
    CAPDU,
    SelectCommand,
    GenerateApplicationCryptogramCommand,
)
from emv.util import unformat_bytes


def test_unmarshal():
    pdu = CAPDU.unmarshal(unformat_bytes("00 A4 04 00 07 A0 00 00 00 03 80 02"))
    assert type(pdu) is SelectCommand
    assert pdu.p1 == 0x04
    assert pdu.p2 == 0x00
    assert len(pdu.data) == 0x07
    assert pdu.le is None

    pdu = CAPDU.unmarshal(
        unformat_bytes(
            """80 AE 80 00 1D 00 00 00 00 00 00 00 00 00 00 00 00
                          00 00 80 00 00 00 00 00 00 01 01 01 00 00 00 00 00"""
        )
    )
    assert type(pdu) is GenerateApplicationCryptogramCommand
    assert pdu.p1 == 0x80
    assert pdu.p2 == 0x00
    assert len(pdu.data) == 0x1D
    assert pdu.le is None
