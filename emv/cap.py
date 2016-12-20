# coding=utf-8
''' EMV-CAP functions. '''
from __future__ import division, absolute_import, print_function, unicode_literals
from .protocol.data import Tag
from .protocol.structures import DOL

# Older cards will respond with an opaque, packed response to the
# application cryptogram request. This DOL lets us deserialise it.
GAC_RESPONSE_DOL = DOL([
    (Tag((0x9F, 0x27)), 1),  # Cryptogram Information Data
    (Tag((0x9F, 0x36)), 2),  # Application Transaction Counter
    (Tag((0x9F, 0x26)), 8),  # Application Cryptogram
    (Tag((0x9F, 0x10)), 7),  # Issuer Application Data
    (Tag(0x90), 0)
])


def get_arqc(app_data):
    # This is the algorithm that barclays_pinsentry.c uses.
    cdol1 = app_data[0x8C]
    data = {
        Tag(0x9A): [0x01, 0x01, 0x01],              # Transaction Date
        Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00]   # Terminal Verification Results
    }

    return cdol1.serialize(data)


def get_cap_value(response):
    ''' Generate a CAP (Pinsentry) value from the ARQC response.

        This algorithm is the one used by barclays-pinsentry.
    '''
    assert 0x80 in response.data or 0x77 in response.data

    if 0x80 in response.data:
        # Response type 1, deserialise it with our static DOL.
        data = GAC_RESPONSE_DOL.unserialise(response.data[0x80])
    elif 0x77 in response.data:
        # Response type 2, TLV format.
        data = response.data[0x77]

    atc = data[(0x9F, 0x36)]  # Application Transaction Counter
    ac = data[(0x9F, 0x26)]   # Application Cryptogram

    result = ((1 << 25) | (atc[1] << 17) | ((ac[5] & 0x01) << 16) | (ac[6] << 8) | ac[7])
    return result
