from NetworkUtilities.utils.errors import IPv4LimitError
from NetworkUtilities.utils.ip_class import FourBytesLiteral
from typing import Dict


class Utils:

    mask_allowed_bytes = [0, 128, 192, 224, 240, 248, 252, 254, 255]
    rfc_allowed_ranges = [
        [192, [168, 168]],
        [172, [16, 31]],
        [10, [0, 255]]
    ]
    rfc_masks = [16, 12, 8]

    @staticmethod
    def switch_length(mask_length: int, index=False) -> int:
        if index:
            return Utils.mask_allowed_bytes.index(mask_length)
        else:
            return Utils.mask_allowed_bytes[mask_length]

    @staticmethod
    def mask_length_to_literal(mask_length: int) -> str:
        result = ''
        if mask_length <= 8:
            result = "{}.0.0.0".format(Utils.switch_length(mask_length))
        elif 8 < mask_length <= 16:
            mask_length -= 8
            result = "255.{}.0.0".format(Utils.switch_length(mask_length))
        elif 16 < mask_length <= 24:
            mask_length -= 16
            result = "255.255.{}.0".format(Utils.switch_length(mask_length))
        elif 24 < mask_length <= 32:
            mask_length -= 24
            result = "255.255.255.{}".format(Utils.switch_length(mask_length))
        return result

    #
    # Getters
    #
    @staticmethod
    def ip_before(ip: FourBytesLiteral) -> FourBytesLiteral:
        def verify(t):
            if t == [0, 0, 0, 0]:
                raise IPv4LimitError("bottom")

        def _check(idx, content):

            if content[idx] == 0:
                content[idx] = 255
                return _check(idx - 1, content)
            else:
                content[idx] = content[idx] - 1
                return content

        ip_ = ip.bytes_list.copy()
        verify(ip_)
        return FourBytesLiteral().set_eval(_check(3, ip_))

    @staticmethod
    def ip_after(ip: FourBytesLiteral) -> FourBytesLiteral:
        def verify(t):
            if t == [255, 255, 255, 255]:
                raise IPv4LimitError("top")

        def _check(idx, content):

            if content[idx] == 255:
                content[idx] = 0
                return _check(idx - 1, content)
            else:
                content[idx] = content[idx] + 1
                return content

        ip_ = ip.bytes_list.copy()
        verify(ip_)
        return FourBytesLiteral().set_eval(_check(3, ip_))

    #
    # Checkers
    #
    @staticmethod
    def ip_in_range(network_range: Dict[str, FourBytesLiteral], ip: FourBytesLiteral) -> bool:
        """
        checks if an ip is in the given network range

        :param network_range: the given network range
        :param ip: the ip that we want to check
        :return bool: if the ip is in the list
        """

        start, end = network_range['start'], network_range['end']
        temp, ip_list = start.__copy__(), []

        ip_list.append(start.bytes_list)
        ip_list.append(end.bytes_list)

        while str(temp) != str(end):
            temp = Utils.ip_after(temp)
            ip_list.append(str(temp))

        return str(ip) in ip_list

    #
    # Others
    #
    @staticmethod
    def to_literal(x):
        return ".".join([str(i) for i in x])

    @staticmethod
    def netr_to_literal(x):
        return {"start": str(x["start"]), "end": str(x['end'])}

    @staticmethod
    def dec_to_bin(x):
        return int(bin(x)[2:])
