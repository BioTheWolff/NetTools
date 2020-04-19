from NetworkUtilities.utils.errors import IPv4LimitError, NetworkLimitException
from NetworkUtilities.utils.ip_class import FourBytesLiteral
from typing import Dict


class Utils:

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
