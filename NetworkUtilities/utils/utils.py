from NetworkUtilities.core.errors import NetworkLimitError, IPOffNetworkRangeException


class Utils:

    #
    # Getters
    #
    @staticmethod
    def ip_before(ip):
        def _check(idx, content):
            if idx == 0 and content[idx] == 0:
                raise NetworkLimitError("bottom")

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
                raise NetworkLimitError("top")

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
            raise IPOffNetworkRangeException()
