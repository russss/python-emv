from emv.util import hex_int


def test_hex_int():
    assert hex_int(123456) == [0x12, 0x34, 0x56]
    assert hex_int(65432) == [0x06, 0x54, 0x32]
