from NetworkUtilities.core.errors import MaskLengthOffBoundsException, \
    RFCRulesWrongCoupleException, \
    RFCRulesIPWrongRangeException, MaskNotProvided, IncorrectMaskException, IPOffNetworkRangeException, \
    BytesLengthException, ByteNumberOffLimitsException
from NetworkUtilities.core.utils import Utils
from typing import Union


class NetworkBasic:
    ip, mask, address_type = None, None, None
    mask_length, addresses = 0, 0
    rfc_current_range, rfc_masks = None, [16, 12, 8]
    rfc_allowed_ranges = [[192, [168, 168]], [172, [16, 31]], [10, [0, 255]]]
    mask_allowed_bytes = [0, 128, 192, 224, 240, 248, 252, 254, 255]
    network_range = {}
    lang_dict = {
        'network': "Network:",
        'cidr': "CIDR : {}/{}",
        'cidr_adv': "CIDR (Classless Inter Domain Routing) : {}/{}",
        'addr_avail': "{} available addresses",
        'addr_avail_advanced': "{} occupied addresses out of {} available addresses",
        'addr_types': {
            'net': "network",
            'mac': "computer",
            'bct': "broadcast"
        },
        'addr_type': "The address {} is a {} address",

        'utils': "{} sub-network{}",
        'sub_addr': "{} - {} ({} addresses)",
        'sub_addr_advanced': "{} - {} ({} available addresses, {} requested)",
        'net_usage': "NetworkBasic usage:"
    }

    #
    # DUNDERS
    #
    def __init__(self, ip: str, mask: Union[str, int] = None) -> None:
        """
        The mask is an optional parameter in case the CIDR is passed into the ip parameter.
        The CIDR, as in its definition, can only be expressed with the mask length:
            - 192.168.1.0/24 is a valid CIDR and will be accepted
            - 192.168.1.0/255.255.255.0 is not a valid CIDR and will raise an Exception

        CIDR informations can be found here: https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing

        :param ip: The ip that starts the range
        :param mask: The mask literal or length
        :raises:
            MaskNotProvided: If the mask parameter is None and the ip parameter is not a valid CIDR

        TODO: delete languages option
        """

        if mask is None:
            try:
                ip, mask = ip.split('/')
                self.ip = ip
                self.mask = mask
            except ValueError:
                raise MaskNotProvided(ip)
        else:
            self.ip = ip
            self.mask = mask

        self._verify_provided_types()
        self.calculate_mask()
        self._verify_rfc_rules()

    #
    # __init__ Tests
    #
    def _verify_provided_types(self) -> None:
        """
        Verifies the provided types (ip, and mask). If a CIDR was passed, the __init__ took care of the spliting into
        respective ip and mask.

        :raises:
            IPBytesLengthException: If the IP block is not 4 bytes long.
            IPByteNumberOffLimitsException: If a byte from the IP is not between 0 and 255
            MaskBytesLengthException! If the mask is not 4 bytes long.
            MaskByteNumberOffLimitsException: If a byte from the mask is not between 0 and 255
            MaskLengthOffBoundsException: If the mask length is not between 0 and 32
        """

        temp = self.ip.split('.')
        if len(temp) != 4:
            raise BytesLengthException('IP', len(temp))
        for e in temp:
            if not (0 <= int(e) <= 255):
                raise ByteNumberOffLimitsException('IP', e, temp.index(e))

        try:
            temp = self.mask.split('.')
            if len(temp) == 1:
                raise AttributeError()
            if len(temp) != 4:
                raise BytesLengthException('mask', len(temp))
            for e in temp:
                if not (0 <= int(e) <= 255):
                    raise ByteNumberOffLimitsException('Mask', e, temp.index(e))
        except (AttributeError, ValueError):
            if 0 <= int(self.mask) <= 32:
                return
            else:
                raise MaskLengthOffBoundsException(self.mask)

    def calculate_mask(self) -> None:
        """
        Calculates the mask from the instance var self.mask

        If the mask is a literal mask (i.e. '255.255.255.0'), the try case is concerned.
        If instead, the user gave the mask length, we make sure to raise an AttributeError to switch to the
        except case to do proper testing.

        :raises:
            IncorrectMaskException: if the mask is wrongly formed (byte != 0 after byte < 255) or if the mask contains a
                byte that cannot be used in a mask.
        """

        try:
            # The mask is given by its literal
            temp = self.mask.split('.')
            if len(temp) == 1:
                # If the mask is given by its length
                # Use AttributeError raise to switch to the except case
                raise AttributeError()

            length = 0

            for byte in range(4):
                concerned = int(temp[byte])
                # We check that the byte is in the awaited bytes list
                if concerned in self.mask_allowed_bytes:
                    # If mask contains a 0, we check that each next byte
                    # contains only a 0, else we raise an IncorrectMaskException
                    if concerned < 255:
                        for i in range(1, 4 - byte):
                            b = temp[byte + i]
                            if b != '0':
                                raise IncorrectMaskException(is_out_allowed=False, value=b, extra=byte + i)

                    length += self._switch_length(concerned, index=True)
                else:
                    raise IncorrectMaskException(is_out_allowed=True, value=concerned)

            # Stock the length
            self.mask_length = length

        except AttributeError:
            # The mask is given by its length
            self.mask_length = int(self.mask)
            self.mask = self.mask_length_to_literal(self.mask_length)

        finally:
            self.addresses = 2 ** (32 - self.mask_length) - 2

    def _verify_rfc_rules(self) -> None:
        """
        Verifies that both the IP and the mask match RFC standards

        For more information on RFC 1918 standards, check https://tools.ietf.org/html/rfc1918

        :raises:
            RFCRulesIPWrongRangeException: If the range is not one of the three stated by RFC 1918:
                - 192.168/16 prefix (IP starting by 192.168 and mask length greater or equal to 16)
                - 172.16/12 prefix (IP starting by 172.16 and mask length greater or equal to 12)
                - 10/8 prefix (IP starting by 10 and mask length greater or equal to 8)
            RFCRulesWrongCoupleException: If the mask length is lesser than the one stated above
        """

        def _check(content):
            ip_test = False
            for I in range(3):
                if (int(content[0]) == self.rfc_allowed_ranges[I][0]) and \
                        (self.rfc_allowed_ranges[I][1][0] <= int(content[1]) <= self.rfc_allowed_ranges[I][1][1]):
                    ip_test = True
                    self.rfc_current_range = I

            if ip_test is False:
                raise RFCRulesIPWrongRangeException(ip[0], ip[1])

        ip = self.ip.split('.')
        mask = self.mask_length

        # We check that ip respects RFC standards
        _check(ip)

        # We then check that provided mask corresponds to RFC standards
        for i in range(3):
            allowed = self.rfc_allowed_ranges[i][0]
            allowed_mask = self.rfc_masks[i]
            if (int(ip[0]) == allowed) and (mask < allowed_mask):
                raise RFCRulesWrongCoupleException(ip[0], ip[1], allowed_mask, mask)

    #
    # Dispatchers
    #   Functions that recieve a complex part excluded from the main function they are called from
    #
    def _switch_length(self, mask_length: int, index=False) -> int:
        if index:
            return self.mask_allowed_bytes.index(mask_length)
        else:
            return self.mask_allowed_bytes[mask_length]

    def mask_length_to_literal(self, mask_length: int) -> str:
        result = ''
        if mask_length <= 8:
            result = "{}.0.0.0".format(self._switch_length(mask_length))
        elif 8 < mask_length <= 16:
            mask_length -= 8
            result = "255.{}.0.0".format(self._switch_length(mask_length))
        elif 16 < mask_length <= 24:
            mask_length -= 16
            result = "255.255.{}.0".format(self._switch_length(mask_length))
        elif 24 < mask_length <= 32:
            mask_length -= 24
            result = "255.255.255.{}".format(self._switch_length(mask_length))
        return result

    #
    # Template for child classes
    #
    def _display(self, machine_ip: str = None):
        print(self.lang_dict['network'])
        print(self.lang_dict['cidr'].format(self.ip, self.mask_length))
        print("{} - {}".format(self.network_range['start'], self.network_range['end']))
        print(self.lang_dict['addr_avail'].format(self.addresses))

        if self.address_type is not None and machine_ip:
            print('')

            if self.address_type in [0, 1, 2]:
                types = ['net', 'mac', 'bct']
                machine_type = self.lang_dict['addr_types'][types[self.address_type]]
            else:
                raise Exception("Given address type other than expected address types")

            print(self.lang_dict['addr_type'].format(machine_ip, machine_type))

    #
    # Main functions
    #
    def determine_network_range(self, start_ip: str = None, machine_bits: int = None, addresses_list: bool = None):
        """

        :param start_ip: The ip we have to start the range from. Used only by the SubnetworkBuilder class
        :param machine_bits: Used to pass machine bits instead of network bits. Used by SubnetworkBuilder class
        :param addresses_list: If one wants the list of each ip constituting the range
        :return:
            result: the determined range
            liste: the list of addresses in the range
        """

        result = None
        start = self.ip if start_ip is None else start_ip
        machine_bits = 32 - self.mask_length if machine_bits is None else machine_bits

        def _check(idx, content):
            Utils.in_rfc_range(self.rfc_current_range, idx, content[idx])

            if content[idx] == 255:
                content[idx] = 0
                return _check(idx - 1, content)
            else:
                content[idx] = content[idx] + 1
                return content

        liste = []

        if start_ip is None and (self.mask_length == self.rfc_masks[self.rfc_current_range]) and addresses_list is None:
            if self.rfc_current_range == 0:
                result = {'start': "192.168.0.0", 'end': "192.168.255.255"}
            elif self.rfc_current_range == 1:
                result = {'start': "172.16.0.0", 'end': "172.31.255.255"}
            elif self.rfc_current_range == 2:
                result = {'start': "10.0.0.0", 'end': "10.255.255.255"}

        else:
            if addresses_list:
                liste.append(start)
            temp_ip = start.split('.')
            addresses = 2 ** machine_bits
            for e in temp_ip:
                temp_ip[temp_ip.index(e)] = int(e)

            # we take 1 from addresses because the starting ip is already one
            for _ in range(addresses - 1):
                temp_ip = _check(3, temp_ip)
                if addresses_list:
                    liste.append(".".join([str(i) for i in temp_ip]))

            for e in temp_ip:
                temp_ip[temp_ip.index(e)] = str(e)

            result = {'start': start, 'end': '.'.join(temp_ip)}

        if not result:
            return

        self.network_range = result
        if addresses_list:
            del liste[-1]
            return result, liste
        else:
            return result

    def determine_type(self, machine_ip: str) -> int:
        """
        Determines the type of the given ip.

        :param machine_ip: The IP we want to have the type of.
        :return:
            address_type: the address type of the machine
        :raises:
            IPOffNetworkRangeException: If the given IP is not in the network range
        """

        if not self.network_range:
            self.determine_network_range()

        if not Utils.ip_in_range(self.network_range, machine_ip):
            raise IPOffNetworkRangeException(machine_ip)

        if self.network_range['start'] == machine_ip:
            self.address_type = 0
        elif self.network_range['end'] == machine_ip:
            self.address_type = 2
        else:
            self.address_type = 1

        return self.address_type


class NetworkBasicDisplayer(NetworkBasic):

    def display_range(self, display=False) -> None:
        self.determine_network_range()

        if display is True:
            self._display()
        else:
            print(self.network_range)

    def display_type(self, machine_ip: str, display=False) -> None:
        self.determine_type(machine_ip)

        if display is True:
            self._display(machine_ip=machine_ip)
        elif display is False:
            if self.address_type == 0:
                machine_type = self.lang_dict['addr_types']['net']
            elif self.address_type == 1:
                machine_type = self.lang_dict['addr_types']['mac']
            elif self.address_type == 2:
                machine_type = self.lang_dict['addr_types']['bct']

            temp = self.network_range
            temp['address_type'] = machine_type
            print(temp)
