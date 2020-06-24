# BYTES LENGTH
class BytesLengthException(Exception):
    def __init__(self, type_, bytes_):
        self.type = type_
        self.bytes = bytes_

    def __repr__(self):
        return f"{self.type} must be 4 bytes long, found {self.bytes} byte(s)."

    def __str__(self):
        return self.__repr__()


# NUMBER OFF LIMITS
class ByteNumberOffLimitsException(Exception):
    def __init__(self, type_, nb, byte):
        self.type = type_
        self.byte = byte
        self.nb = nb

    def __repr__(self):
        return f"{self.type} bytes must be between 0 and 255. Found {self.nb} at byte {self.byte}"

    def __str__(self):
        return self.__repr__()


# OFF NETWORK RANGE
class IPOffNetworkRangeException(Exception):
    def __init__(self, ip):
        self.ip = ip

    def __repr__(self):
        return f"IP address {self.ip} not in network range."

    def __str__(self):
        return self.__repr__()


# MASK SPECIFIC ERRORS
class MaskNotProvided(Exception):
    def __init__(self, cidr):
        self.cidr = cidr

    def __repr__(self):
        return f"Could not find IP and mask in given cidr {self.cidr}"

    def __str__(self):
        return self.__repr__()


class MaskLengthOffBoundsException(Exception):
    def __init__(self, length):
        self.length = length

    def __repr__(self):
        return f"Provided mask length ({self.length}) out of bounds [0-32]"

    def __str__(self):
        return self.__repr__()


class IncorrectMaskException(Exception):
    def __init__(self, is_out_allowed, value, extra=None):
        self.is_out_allowed = is_out_allowed
        self.value = value
        self.extra = extra

    def __repr__(self):
        if self.is_out_allowed:
            # Value out of allowed values list
            return f"Incorrect mask. Allowed values are [0,128,192,224,240,248,242,254,255], found {self.value}"
        else:
            # Mask byte not empty after byte < 255
            return f"Mask bytes must all be empty (0) after a byte with a value under 255, found {self.value} " \
                   f"at byte {self.extra}"

    def __str__(self):
        return self.__repr__()


class MaskTooSmallException(Exception):
    def __init__(self, given, advised):
        self.given = given
        self.advised = advised

    def __repr__(self):
        return f"Given mask length ({self.given}) cannot handle all the addresses of the subnetworks. " \
               f"Advised length : {self.advised}"

    def __str__(self):
        return self.__repr__()


# RFC EXCEPTIONS
class RFCRulesIPWrongRangeException(Exception):
    def __init__(self, first, second):
        self.f = first
        self.s = second

    def __repr__(self):
        return f"IP must be either 192.168.x.x , 172.16.x.x or 10.0.x.x; found {self.f}.{self.s}.x.x"

    def __str__(self):
        return self.__repr__()


class RFCRulesWrongCoupleException(Exception):
    def __init__(self, first, second, required, given):
        self.f = first
        self.s = second
        self.r = required
        self.g = given

    def __repr__(self):
        return f"According to RFC standards, given couple must be {self.f}.{self.s}.x.x/>={self.r}, " \
               f"found mask length {self.g}"

    def __str__(self):
        return self.__repr__()


# NETWORK LIMIT
class NetworkLimitException(Exception):
    def __repr__(self):
        return "RFC range limit reached while trying to determine network range."

    def __str__(self):
        return self.__repr__()


class IPv4LimitError(Exception):

    def __init__(self, type_):
        self.type = type_
        if type_ == 'bottom':
            self.display = "0.0.0.0"
        elif type_ == 'top':
            self.display = "255.255.255.255"

    def __repr__(self):
        return f"IPv4 {self.type} limit ({self.display}) reached"

    def __str__(self):
        return self.__repr__()
