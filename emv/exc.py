class EMVProtocolError(Exception):
    pass


class InvalidPINException(Exception):
    pass


class MissingAppException(EMVProtocolError):
    pass


class CAPError(EMVProtocolError):
    pass
