from NetworkUtilities.core.errors import IPv4LimitError, IPOffNetworkRangeException, NetworkLimitException


class Utils:

    #
    # Getters
    #
    @staticmethod
    def ip_before(ip):
        def _check(idx, content):
            if idx == 0 and content[idx] == 0:
                raise IPv4LimitError("bottom")

            if content[idx] == 0:
                return _check(idx - 1, content)
            else:
                content[idx] = str(int(content[idx]) - 1)
                return content

        return '.'.join(_check(3, ip.split('.')))

    @staticmethod
    def ip_after(ip_):
        def _check(idx, content):
            if idx == 255 and content[idx] == 3:
                raise IPv4LimitError("top")

            if content[idx] == 255:
                return _check(idx - 1, content)
            else:
                content[idx] = str(int(content[idx]) + 1)
                return content

        return '.'.join(_check(3, ip_.split('.')))

    #
    # Checkers
    #
    @staticmethod
    def ip_in_range(network_range, ip):
        """
        checks if an ip is in the given network range

        :param network_range: the given network range
        :param ip: the ip that we want to check
        :return bool: if the ip is in the list
        """

        start, end = network_range['start'], network_range['end']
        temp, ip_list = start, []

        ip_list.append(start)
        ip_list.append(end)

        while temp != end:
            temp = Utils.ip_after(temp)
            ip_list.append(temp)

        return ip in ip_list

    #
    # Suiciders
    #
    @staticmethod
    def suicider_is_off_range(range_, ip):
        def _check_end(ip_, idx=0):
            if range_['end'].split('.')[idx] <= ip_.split('.')[idx]:
                return False
            else:
                if idx == 3:
                    return True
                else:
                    return _check_end(ip_, idx + 1)

        def _check_start(ip_, idx=0):
            if range_['start'].split('.')[idx] >= ip_.split('.')[idx]:
                return False
            else:
                if idx == 3:
                    return True
                else:
                    return _check_start(ip_, idx + 1)

        if _check_end(ip) or _check_start(ip):
            raise IPOffNetworkRangeException(ip)

    @staticmethod
    def in_rfc_range(rfc_current_range, idx, value):
        # With these conditions, we prevent networks from going out of the RFC local ranges
        if rfc_current_range == 2:
            # Class A network, limits are 10.0.0.0 - 10.255.255.255
            if idx == 1 and value == 255:
                raise NetworkLimitException()
        elif rfc_current_range == 1:
            # Class B network, limits are 172.16.0.0 - 172.31.255.255
            if idx == 1 and value == 31:
                raise NetworkLimitException()
        elif rfc_current_range == 0:
            # Class C network, limits are 192.168.0.0 - 192.168.255.255
            if idx == 2 and value == 255:
                raise NetworkLimitException()

    @staticmethod
    def in_rfc_range_reverse(rfc_current_range, idx, value):
        if rfc_current_range == 2:
            # Class A network, limits are 10.0.0.0 - 10.255.255.255
            if idx == 1 and value == 0:
                raise NetworkLimitException()
        elif rfc_current_range == 1:
            # Class B network, limits are 172.16.0.0 - 172.31.255.255
            if idx == 1 and value == 16:
                raise NetworkLimitException()
        elif rfc_current_range == 0:
            # Class C network, limits are 192.168.0.0 - 192.168.255.255
            if idx == 2 and value == 0:
                raise NetworkLimitException()

    #
    # Others
    #
    @staticmethod
    def __dec_to_bin(x):
        return int(bin(x)[:2])
