from NetworkUtilities.core.errors import MaskLengthOffBoundsException, MaskByteNumberOffLimitsException, \
    IPBytesLengthException, MaskBytesLengthException, IPByteNumberOffLimitsException, RFCRulesWrongCoupleException, \
    RFCRulesIPWrongRangeException, MaskNotProvided, IncorrectMaskException, IPOffNetworkRangeException, \
    NetworkLimitException
from NetworkUtilities.core.utils import Utils


class NetworkBasic:
    lang = 'en'
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
    error_dict = {
        'ip_bytes_length': "IP must be 4 bytes long, found {} byte(s)",
        'ip_number_off_limits': "IP bytes must be between 0 and 255. Found {} at byte {}",
        'ip_off_network_range': "IP address not in network range.",

        'mask_bytes_length': "Mask must be 4 bytes long, found {} bytes",
        'mask_number_off_limits': "Mask bytes must be between 0 and 255. Found {} at byte {}",
        'mask_length_off_bounds': "Provided mask length ({}) out of bounds [0-32]",
        'mask_incorrect': "Incorrect mask. Allowed values: [0,128,192,224,240,248,242,254,255]",
        'mask_too_small': "Given mask length ({}) cannot handle all the addresses of the subnetworks. "
                          "Advised length : {}",

        'rfc_ip_wrong_range': "IP must be either 192.168.x.x , 172.16.x.x or 10.0.x.x; found {}.{}.x.x",
        'rfc_couple': "According to RFC standards, given couple must be {}.{}.x.x/>={}, found mask length {}",
        'rfc_ips_diff_network': "Starting IP ({}) and IP ({}) are not on the same local network",

        'network_limit': "Limit 255.255.255.255 reached while trying to determine (sub)network range."
    }

    #
    # DUNDERS
    #
    def __init__(self, ip, mask=None):
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
    def _verify_provided_types(self):
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
            raise IPBytesLengthException(self.lang, len(temp))
        for e in temp:
            if not (0 <= int(e) <= 255):
                raise IPByteNumberOffLimitsException(self.lang, e, temp.index(e))

        try:
            temp = self.mask.split('.')
            if len(temp) == 1:
                raise AttributeError()
            if len(temp) != 4:
                raise MaskBytesLengthException(self.lang, len(temp))
            for e in temp:
                if not (0 <= int(e) <= 255):
                    raise MaskByteNumberOffLimitsException(self.lang, e, temp.index(e))
        except (AttributeError, ValueError):
            if 0 <= int(self.mask) <= 32:
                return
            else:
                raise MaskLengthOffBoundsException(self.lang, self.mask)

    def calculate_mask(self):
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
                            if temp[byte + i] != '0':
                                raise IncorrectMaskException(self.lang)

                    length += self._switch_length(concerned, index=True)
                else:
                    raise IncorrectMaskException(self.lang)

            # Stock the length
            self.mask_length = length

        except AttributeError:
            # The mask is given by its length
            self.mask_length = int(self.mask)
            self.mask = self.mask_length_to_literal(self.mask_length)

        finally:
            self.addresses = 2 ** (32 - self.mask_length) - 2

    def _verify_rfc_rules(self):
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
                raise RFCRulesIPWrongRangeException(self.lang, ip[0], ip[1])

        ip = self.ip.split('.')
        mask = self.mask_length

        # We check that ip respects RFC standards
        _check(ip)

        # We then check that provided mask corresponds to RFC standards
        for i in range(3):
            allowed = self.rfc_allowed_ranges[i][0]
            allowed_mask = self.rfc_masks[i]
            if (int(ip[0]) == allowed) and (mask < allowed_mask):
                raise RFCRulesWrongCoupleException(self.lang, ip[0], ip[1], allowed_mask, mask)

    #
    # Dispatchers
    #   Functions that recieve a complex part excluded from the main function they are called from
    #
    def _switch_length(self, mask_length, index=False):
        if index:
            return self.mask_allowed_bytes.index(mask_length)
        else:
            return self.mask_allowed_bytes[mask_length]

    def mask_length_to_literal(self, mask_length):
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
    def _display(self, machine_ip=None, is_prober=False):
        print(self.lang_dict['network'])
        print(self.lang_dict['cidr'].format(self.ip, self.mask_length))
        if is_prober:
            print("Estimated range from probing : {} - {}".format(self.network_range['start'],
                                                                  self.network_range['end']))
        else:
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
    def determine_network_range(self, start_ip=None, machine_bits=None, addresses_list=None):
        """

        :param start_ip: The ip we have to start the range from. Used only by the SubnetworkBuilder class
        :param machine_bits: Used to pass machine bits instead of network bits. Used by SubnetworkBuilder class
        :param addresses_list: If one wants the list of each ip constituting the range
        :return:
            result: the determined range
            liste: the list of addresses in the range
        """

        start = self.ip if start_ip is None else start_ip
        machine_bits = 32 - self.mask_length if machine_bits is None else machine_bits

        def _check(idx, content):
            # With these conditions, we prevent networks from going out of the RFC local ranges
            if self.rfc_current_range == 2:
                # Class A network, limits are 10.0.0.0 - 10.255.255.255
                if idx == 1 and content[idx] == 255:
                    raise NetworkLimitException(self.lang)
            elif self.rfc_current_range == 1:
                # Class B network, limits are 172.16.0.0 - 172.31.255.255
                if idx == 1 and content[idx] == 31:
                    raise NetworkLimitException(self.lang)
            elif self.rfc_current_range == 0:
                # Class C network, limits are 192.168.0.0 - 192.168.255.255
                if idx == 2 and content[idx] == 255:
                    raise NetworkLimitException(self.lang)

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
                raise Exception("Something wrong happened when nothing should. Try contacting the author to solve this")

        else:
            if addresses_list:
                liste.append(start)
            ip = start.split('.')
            addresses = 2 ** machine_bits
            for e in ip:
                ip[ip.index(e)] = int(e)

            # we take 1 from addresses because the starting ip is already one
            for _ in range(addresses - 1):
                ip = _check(3, ip)
                if addresses_list:
                    liste.append(".".join([str(i) for i in ip]))

            for e in ip:
                ip[ip.index(e)] = str(e)

            result = {'start': start, 'end': '.'.join(ip)}

        self.network_range = result
        if addresses_list:
            del liste[-1]
            return result, liste
        else:
            return result

    def determine_type(self, machine_ip):
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
            raise IPOffNetworkRangeException(self.lang)

        if self.network_range['start'] == machine_ip:
            self.address_type = 0
        elif self.network_range['end'] == machine_ip:
            self.address_type = 2
        else:
            self.address_type = 1

        return self.address_type


class NetworkBasicDisplayer(NetworkBasic):

    def display_range(self, display=False):
        self.determine_network_range()

        if display is True:
            self._display()
        else:
            print(self.network_range)

    def display_type(self, machine_ip, display=False):
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
            else:
                raise Exception("Given address type other than expected address types")

            temp = self.network_range
            temp['address_type'] = machine_type
            print(temp)
