''' EMV Chip Authentication Program, a.k.a DPA, a.k.a Pinsentry.

    There is no public specification for the EMV CAP "standard". The code in this
    module is based on a number of other hacky projects. It works for Barclays
    cards in the UK. It will probably work for other UK cards as there is a
    UK-wide standard.

    I make no guarantees for non-UK cards as I'm aware that certain banks have
    made their own "customisations" to EMV CAP.
'''
from .protocol.data import Tag
from .protocol.command import GenerateApplicationCryptogramCommand
from .protocol.structures import DOL
from .exc import CAPError
from .util import hex_int

# Older cards will respond with an opaque, packed response to the
# application cryptogram request. This DOL lets us deserialise it.
GAC_RESPONSE_DOL = DOL([
    (Tag((0x9F, 0x27)), 1),  # Cryptogram Information Data
    (Tag((0x9F, 0x36)), 2),  # Application Transaction Counter
    (Tag((0x9F, 0x26)), 8),  # Application Cryptogram
    (Tag((0x9F, 0x10)), 7),  # Issuer Application Data
    (Tag(0x90), 0)
])


def get_arqc_req(app_data, value=None, challenge=None):
    ''' Generate the data to send with the generate application cryptogram request.
        This data is in the format requested by the card in the CDOL1 field of the
        application data.

        This is the algorithm that barclays_pinsentry.c uses.
    '''
    if Tag.CDOL1 not in app_data:
        raise CAPError("Application data doesn't include CDOL1 field: %r" % app_data)

    cdol1 = app_data[Tag.CDOL1]
    data = {
        Tag(0x9A): [0x01, 0x01, 0x01],              # Transaction Date
        Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00]   # Terminal Verification Results
    }

    if challenge is not None:
        # If an account number (or challenge) is provided, it goes in the
        # "unpredictable number" field.
        data[Tag((0x9F, 0x37))] = hex_int(challenge)

    if value is not None:
        # If a monetary value is provided, it goes in the "Amount, Authorised"
        # field.
        data[Tag((0x9F, 0x02))] = hex_int(int(round(float(value) * 100, 0)))

    return GenerateApplicationCryptogramCommand(GenerateApplicationCryptogramCommand.ARQC,
                                                cdol1.serialise(data))


def get_cap_value(response):
    ''' Generate a CAP value from the ARQC response.

        This algorithm is the one used by barclays-pinsentry.c, but this will only work
        for a subset of cards.

        The proper way to do this is to use the Issuer Proprietary Bitmap from the
        application data response. Most UK issuers seem to use the same IPB though.

        c.f. https://github.com/zoobab/EMVCAP/blob/master/EMVCAPcore.py#L507
    '''

    if Tag.RMTF1 in response.data:
        # Response type 1, deserialise it with our static DOL.
        data = GAC_RESPONSE_DOL.unserialise(response.data[Tag.RMTF1])
    elif Tag.RMTF2 in response.data:
        # Response type 2, TLV format.
        data = response.data[Tag.RMTF2]
    else:
        raise CAPError("Unknown response type in ARQC response: %s" % response.data)

    atc = data[Tag.ATC]       # Application Transaction Counter
    ac = data[(0x9F, 0x26)]   # Application Cryptogram

    # The bitshift magic below *probably* corresponds to the IPB from Barclays cards:
    # CID = I, ATC = A, AC = C, IAD = D
    #
    # II AA AA CC CC CC CC CC CC CC CC DD DD DD DD DD DD DD DD DD DD DD...
    # 80 00 FF 00 00 00 00 00 01 FF FF 00 00 00 00 00 00 00

    result = ((1 << 25) | (atc[1] << 17) | ((ac[5] & 0x01) << 16) | (ac[6] << 8) | ac[7])
    return result
