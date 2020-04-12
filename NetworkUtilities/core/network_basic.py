from NetworkUtilities.utils.errors import MaskLengthOffBoundsException, \
    RFCRulesWrongCoupleException, \
    RFCRulesIPWrongRangeException, MaskNotProvided, IncorrectMaskException, BytesLengthException, ByteNumberOffLimitsException
from NetworkUtilities.utils.utils import Utils
from typing import Union, List


class NetworkBasic:
    ip: List[int] = None
    mask: Union[List[int], str] = None
    address_type = None
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
        'addr_avail_advanced': "addresses: {} occupied / {} available",
        'addr_types': {
            'net': "network",
            'mac': "computer",
            'bct': "broadcast"
        },
        'addr_type': "The address {} is a {} address",

        'utils': "{} sub-network{}",
        'sub_addr': "{} - {} ({} addresses)",
        'sub_addr_advanced': "{} - {} ({} available addresses, {} requested)",
        'net_usage': "Network usage:"
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

        :param ip: The ip in the range
        :param mask: The mask literal or length
        :raises:
            MaskNotProvided: If the mask parameter is None and the ip parameter is not a valid CIDR

        TODO: delete languages option
        """

        if mask is None:
            try:
                ip, mask = ip.split('/')
                self.ip = [int(i) for i in ip.split('.')]
                self.mask = mask
            except ValueError:
                raise MaskNotProvided(ip)
        else:
            self.ip = [int(i) for i in ip.split('.')]
            self.mask = mask

        self._verify_provided_types()
        self.calculate_mask()
        self._verify_rfc_rules()

        self.determine_network_range()

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

        temp = self.ip
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
            self.mask = [int(i) for i in temp]

        except AttributeError:
            # The mask is given by its length
            self.mask_length = int(self.mask)
            self.mask = [int(i) for i in self.mask_length_to_literal(self.mask_length).split('.')]

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

        ip = self.ip
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
    def _display(self):
        literal_netr = {"start": Utils.to_literal(self.network_range['start']),
                        "end": Utils.to_literal(self.network_range['end'])}
        literal_ip = Utils.to_literal(self.ip)

        print(self.lang_dict['network'])
        print(self.lang_dict['cidr'].format(literal_ip, self.mask_length))
        print("{} - {}".format(literal_netr['start'], literal_netr['end']))
        print(self.lang_dict['addr_avail'].format(self.addresses))
        print('')

        self.determine_type()
        if self.address_type in [0, 1, 2]:
            types = ['net', 'mac', 'bct']
            machine_type = self.lang_dict['addr_types'][types[self.address_type]]
        else:
            raise Exception("Given address type other than expected address types")

        print(self.lang_dict['addr_type'].format(literal_ip, machine_type))

    #
    # Main functions
    #
    def determine_network_range(self, ip: List[int] = None, machine_bits: int = None):

        ip_ = ip if ip else self.ip
        mask = [int(i) for i in
                self.mask_length_to_literal(32 - machine_bits).split('.')
                ] if machine_bits else self.mask

        # Network address
        net = []
        for i in range(4):
            net.append(ip_[i] & mask[i])

        # Broadcast address
        bct = []
        for i in range(4):
            bct.append(ip_[i] | (255 ^ mask[i]))

        result = {"start": net, "end": bct}

        if ip is None and machine_bits is None:
            self.network_range = result

        return result

    def determine_type(self) -> int:
        """
        Determines the type of the given ip.

        :return:
            address_type: the address type of the machine
        :raises:
            IPOffNetworkRangeException: If the given IP is not in the network range
        """

        res = self.determine_network_range()

        if res['start'] == self.ip:
            self.address_type = 0
        elif res['end'] == self.ip:
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
            print(Utils.netr_to_literal(self.network_range))

    def display_type(self, display=False) -> None:
        self.determine_type()

        if display is True:
            self._display()
        elif display is False:
            if self.address_type == 0:
                machine_type = self.lang_dict['addr_types']['net']
            elif self.address_type == 1:
                machine_type = self.lang_dict['addr_types']['mac']
            elif self.address_type == 2:
                machine_type = self.lang_dict['addr_types']['bct']
            else:
                machine_type = None

            temp = Utils.netr_to_literal(self.network_range)
            temp['address_type'] = machine_type
            print(temp)
