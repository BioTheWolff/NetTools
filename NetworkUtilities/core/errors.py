# BYTES LENGTH
class IPBytesLengthException(Exception):
    def __init__(self, lang, bytes_):
        self.lang = lang
        self.bytes = bytes_

    def __repr__(self):
        if self.lang == 'raw':
            return self.bytes
        elif self.lang == 'fr':
            return f"L'IP doit faire 4 octets, trouvé {self.bytes} octect(s)"
        else:
            return f"IP must be 4 bytes long, found {self.bytes} byte(s)"


class MaskBytesLengthException(Exception):
    def __init__(self, lang, bytes_):
        self.lang = lang
        self.bytes = bytes_

    def __repr__(self):
        if self.lang == 'raw':
            return self.bytes
        elif self.lang == 'fr':
            return f"Le masque doit faire 4 octets, trouvé {self.bytes} octect(s)"
        else:
            return f"Mask must be 4 bytes long, found {self.bytes} byte(s)"


# NUMBER OFF LIMITS
class IPByteNumberOffLimitsException(Exception):
    def __init__(self, lang, nb, byte):
        self.lang = lang
        self.nb = nb
        self.byte = byte

    def __repr__(self):
        if self.lang == 'raw':
            return {'byte': self.byte, 'number': self.nb}
        elif self.lang == 'fr':
            return f"Les octects de l'IP doivent être entre 0 et 255. Trouvé {self.nb} à l'octect {self.byte}"
        else:
            return f"IP bytes must be between 0 and 255. Found {self.nb} at byte {self.byte}"


class MaskByteNumberOffLimitsException(Exception):
    def __init__(self, lang, nb, byte):
        self.lang = lang
        self.nb = nb
        self.byte = byte

    def __repr__(self):
        if self.lang == 'raw':
            return {'byte': self.byte, 'number': self.nb}
        elif self.lang == 'fr':
            return f"Les octects du masque doivent être entre 0 et 255. Trouvé {self.nb} à l'octect {self.byte}"
        else:
            return f"Mask bytes must be between 0 and 255. Found {self.nb} at byte {self.byte}"


# OFF NETWORK RANGE
class IPOffNetworkRangeException(Exception):
    def __init__(self, lang='en'):
        self.lang = lang

    def __repr__(self):
        if self.lang == 'fr':
            return "L'adresse IP n'est pas dans la plage réseau."
        else:
            return "IP address not in network range."


# MASK SPECIFIC ERRORS
class MaskNotProvided(Exception):
    def __init__(self, cidr):
        self.cidr = cidr

    def __repr__(self):
        return f"Could not find IP and mask in given cidr {self.cidr}"


class MaskLengthOffBoundsException(Exception):
    def __init__(self, lang, length):
        self.lang = lang
        self.length = length

    def __repr__(self):
        if self.lang == 'raw':
            return self.length
        elif self.lang == 'fr':
            return f"Longueur du masque ({self.length}) hors limites [0-32]"
        else:
            return f"Provided mask length ({self.length}) out of bounds [0-32]"


class IncorrectMaskException(Exception):
    def __init__(self, lang):
        self.lang = lang

    def __repr__(self):
        if self.lang == 'fr':
            return "Masque incorrect. Valeurs acceptées: [0,128,192,224,240,248,242,254,255"
        else:
            return "Incorrect mask. Allowed values: [0,128,192,224,240,248,242,254,255]"


class MaskTooSmallException(Exception):
    def __init__(self, lang, given, advised):
        self.lang = lang
        self.given = given
        self.advised = advised

    def __repr__(self):
        if self.lang == 'raw':
            return {'given': self.given, 'advised': self.advised}
        elif self.lang == 'fr':
            return f"La longueur du masque donnée ({self.given}) ne peut contenir toutes les adresses des " \
                   f"sous-réseaux. Longueur conseillée : {self.advised}"
        else:
            return f"Given mask length ({self.given}) cannot handle all the addresses of the subnetworks. " \
                   f"Advised length : {self.advised}"


# RFC EXCEPTIONS
class RFCRulesIPWrongRangeException(Exception):
    def __init__(self, lang, first, second):
        self.lang = lang
        self.f = first
        self.s = second

    def __repr__(self):
        if self.lang == 'raw':
            return {'first': self.f, 'second': self.s}
        elif self.lang == 'fr':
            return f"L'IP doit être sous la forme 192.168.x.x , 172.16.x.x ou 10.0.x.x; trouvé {self.f}.{self.s}.x.x"
        else:
            return f"IP must be either 192.168.x.x , 172.16.x.x or 10.0.x.x; found {self.f}.{self.s}.x.x"


class RFCRulesWrongCoupleException(Exception):
    def __init__(self, lang, first, second, required, given):
        self.lang = lang
        self.f = first
        self.s = second
        self.r = required
        self.g = given

    def __repr__(self):
        if self.lang == 'raw':
            return {'first': self.f, 'second': self.s, 'required': self.r, 'given': self.g}
        elif self.lang == 'fr':
            return f"Selon les standards RFC, le couple doit être {self.f}.{self.s}.x.x/>={self.r}, " \
                   f"trouvé masque de longueur {self.g}"
        else:
            return f"According to RFC standards, given couple must be {self.f}.{self.s}.x.x/>={self.r}, " \
                   f"found mask length {self.g}"


class RFCRulesIPsNetworksDifferException(Exception):
    def __init__(self, lang, first, second):
        self.lang = lang
        self.f = first
        self.s = second

    def __repr__(self):
        if self.lang == 'raw':
            return {'first': self.f, 'second': self.s}
        elif self.lang == 'fr':
            return f"L'IP de départ ({self.f}) et l'IP ({self.s}) ne sont pas sur le même réseau local"
        else:
            return f"Starting IP ({self.f}) and IP ({self.s}) are not on the same local network"


# NETWORK LIMIT
class NetworkLimitException(Exception):
    def __init__(self, lang):
        self.lang = lang

    def __repr__(self):
        if self.lang == 'fr':
            return "Limite 255.255.255.255 atteinte en essayant de définir une plage (de sous-)réseau."
        else:
            return "Limit 255.255.255.255 reached while trying to determine (sub)network range."


class NetworkLimitError(Exception):

    def __init__(self, type_):
        self.type = type_
        if type_ == 'bottom':
            self.display = "0.0.0.0"
        elif type_ == 'top':
            self.display = "255.255.255.255"

    def __str__(self):
        return f"Network {self.type} limit ({self.display}) reached"
