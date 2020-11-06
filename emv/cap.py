""" EMV Chip Authentication Program, a.k.a DPA, a.k.a Pinsentry.

    There is no public specification for the EMV CAP "standard". The code in this
    module is based on a number of other hacky projects. It works for most UK cards.

    I make no guarantees for non-UK cards as I'm aware that certain banks have
    made their own "customisations" to EMV CAP.
"""
from .protocol.data import Tag
from .protocol.command import GenerateApplicationCryptogramCommand
from .protocol.structures import DOL
from .exc import CAPError
from .util import hex_int

# Older cards will respond with an opaque, packed response to the
# application cryptogram request. This DOL lets us deserialise it.
GAC_RESPONSE_DOL = DOL(
    [
        (Tag((0x9F, 0x27)), 1),  # Cryptogram Information Data
        (Tag((0x9F, 0x36)), 2),  # Application Transaction Counter
        (Tag((0x9F, 0x26)), 8),  # Application Cryptogram
        (Tag((0x9F, 0x10)), 7),  # Issuer Application Data
        (Tag(0x90), 0),
    ]
)


def get_arqc_req(app_data, value=None, challenge=None):
    """Generate the data to send with the generate application cryptogram request.
    This data is in the format requested by the card in the CDOL1 field of the
    application data.

    This is the algorithm that barclays_pinsentry.c uses.
    """
    if Tag.CDOL1 not in app_data:
        raise CAPError("Application data doesn't include CDOL1 field: %r" % app_data)

    cdol1 = app_data[Tag.CDOL1]
    data = {
        Tag(0x9A): [0x01, 0x01, 0x01],  # Transaction Date
        Tag(0x95): [0x80, 0x00, 0x00, 0x00, 0x00],  # Terminal Verification Results
    }

    if challenge is not None:
        # If an account number (or challenge) is provided, it goes in the
        # "unpredictable number" field.
        data[Tag((0x9F, 0x37))] = hex_int(challenge)

    if value is not None:
        # If a monetary value is provided, it goes in the "Amount, Authorised"
        # field.
        data[Tag((0x9F, 0x02))] = hex_int(int(round(float(value) * 100, 0)))

    return GenerateApplicationCryptogramCommand(
        GenerateApplicationCryptogramCommand.ARQC, cdol1.serialise(data)
    )


def get_cap_value(response, ipb, psn):
    """Generate a CAP value from the ARQC response.

    The ARQC response is traditionally a data structure returned to the terminal by the
    card during a payment transaction. CAP (mis)uses it to generate an 8-digit one-time
    code. This is done by bitwise masking the values in this structure with the Issuer
    Proprietary Bitmap (IPB) provided by the card in the Application Data structure.
    """

    if Tag.RMTF1 in response.data:
        # Response type 1, deserialise it with our static DOL.
        data = GAC_RESPONSE_DOL.unserialise(response.data[Tag.RMTF1])
    elif Tag.RMTF2 in response.data:
        # Response type 2, TLV format.
        data = response.data[Tag.RMTF2]
    else:
        raise CAPError("Unknown response type in ARQC response: %s" % response.data)

    # IPB acts as a binary mask for the response, where the '0' positions are
    # ignored, and the remaining '1' positions are concatenated, for example:
    # Response: 00101101110100101010010101010101001
    # IPB:      00000111100000000111111110000000000
    # Result:        1011        00101010
    # Concat'd: 101100101010
    # Decimal:  2858

    # Get response data into single list, in the same format as IPB
    resp_data = [item for sublist in data.values() for item in sublist]

    # If the PAN Sequence Number is set, then prepend it to the response data
    if psn is not None:
        resp_data = psn + resp_data

    # Initialise empty string to hold binary result of masking process
    binary_string = ""

    # Iterate through the items in the IPB mask (in reverse)
    for i in reversed(range(0, min(len(ipb), len(resp_data)))):
        # Get the values of data and mask for the current iteration
        data_number = resp_data[i]
        ipb_number = ipb[i]
        # If the mask has some 1s in it
        while ipb_number > 0:
            # Check if the last digit in the binary representation of the mask is '1'
            if ipb_number & 1:
                # And if it is, prepend the last binary digit of the data to the binary string
                binary_string = str(data_number & 1) + binary_string
            # Bitshift both the data and the mask to the right by one bit
            ipb_number >>= 1
            data_number >>= 1

    # And return the binary string converted to a decimal number
    return int(binary_string, 2)
