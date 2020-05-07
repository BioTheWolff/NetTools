from NetworkUtilities.utils.errors import MaskLengthOffBoundsException, \
    RFCRulesWrongCoupleException, \
    RFCRulesIPWrongRangeException, MaskNotProvided, IncorrectMaskException, BytesLengthException, \
    ByteNumberOffLimitsException
from NetworkUtilities.utils.utils import Utils
from NetworkUtilities.utils.ip_class import FourBytesLiteral
from typing import Union, Dict


class IPv4Network:
    ip: FourBytesLiteral = None
    mask: Union[FourBytesLiteral, str] = None

    address_type = None
    mask_length, addresses = 0, 0

    rfc_current_range, rfc_masks = None, [16, 12, 8]
    rfc_allowed_ranges = [
        [192, [168, 168]],
        [172, [16, 31]],
        [10, [0, 255]]
    ]

    network_range: Dict[str, FourBytesLiteral] = {}
    lang_dict = {
        'network': "Network:",
        'cidr': "CIDR : {}/{}",
        'cidr_adv': "CIDR (Classless Inter Domain Routing) : {}/{}",
        'addr_avail': "{} total addresses",
        'addr_avail_advanced': "addresses: {} occupied / {} total",
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

    @property
    def displayable_network_range(self):
        return Utils.netr_to_literal(self.network_range)

    @property
    def displayable_address_type(self):
        li = [
            self.lang_dict['addr_types']['net'],
            self.lang_dict['addr_types']['mac'],
            self.lang_dict['addr_types']['bct']
        ]
        return li[self.address_type]

    #
    # POSSIBLE INITS (built to chain)
    #
    def init_from_couple(self, ip: str, mask: Union[str, int]):
        self.ip = FourBytesLiteral().set_from_string_literal(ip)
        self.mask = mask

        # init "footer". All inits possess this footer to ensure both flow and instance returning
        self.__flow()
        return self

    def init_from_cidr(self, cidr: str):
        try:
            ip, mask = cidr.split('/')
            self.ip = FourBytesLiteral().set_from_string_literal(ip)
            self.mask = mask
        except ValueError:
            raise MaskNotProvided(cidr)

        self.__flow()
        return self

    def init_from_fbl(self, ip: FourBytesLiteral, mask: FourBytesLiteral):
        self.ip = ip
        self.mask = mask

        self.__flow()
        return self

    #
    # init flow
    #
    def __flow(self):
        # Flow function is created to simplify code.
        # All the inits use the same flow, so I found useful to put all of that in one function

        self.__verify_provided_types()
        self.__calculate_mask()
        self.__verify_rfc_rules()

        self.__determine_network_range()
        self.__determine_type()

    def __verify_provided_types(self) -> None:
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

    def __calculate_mask(self) -> None:
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
                if concerned in Utils.mask_allowed_bytes:
                    # If mask contains a 0, we check that each next byte
                    # contains only a 0, else we raise an IncorrectMaskException
                    if concerned < 255:
                        for i in range(1, 4 - byte):
                            b = temp[byte + i]
                            if b != '0':
                                raise IncorrectMaskException(is_out_allowed=False, value=b, extra=byte + i)

                    length += Utils.switch_length(concerned, index=True)
                else:
                    raise IncorrectMaskException(is_out_allowed=True, value=concerned)

            # Stock the length
            self.mask_length = length
            self.mask = FourBytesLiteral().set_from_string_literal(".".join(temp))

        except AttributeError:
            # The mask is given by its length
            self.mask_length = int(self.mask)
            self.mask = FourBytesLiteral().set_from_string_literal(Utils.mask_length_to_literal(self.mask_length))

        finally:
            self.addresses = 2 ** (32 - self.mask_length) - 2

    def __verify_rfc_rules(self) -> None:
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
            for i_ in range(3):
                if (int(content[0]) == self.rfc_allowed_ranges[i_][0]) and \
                        (self.rfc_allowed_ranges[i_][1][0] <= int(content[1]) <= self.rfc_allowed_ranges[i_][1][1]):
                    ip_test = True
                    self.rfc_current_range = i_

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
    # Template for child classes
    #
    def _display(self):
        literal_netr = self.displayable_network_range
        literal_ip = str(self.ip)

        print(self.lang_dict['network'])
        print(self.lang_dict['cidr'].format(literal_ip, self.mask_length))
        print("{} - {}".format(literal_netr['start'], literal_netr['end']))
        print(self.lang_dict['addr_avail'].format(self.addresses))
        print('')

        self.__determine_type()
        if self.address_type in [0, 1, 2]:
            types = ['net', 'mac', 'bct']
            machine_type = self.lang_dict['addr_types'][types[self.address_type]]
        else:
            raise Exception("Given address type other than expected address types")

        print(self.lang_dict['addr_type'].format(literal_ip, machine_type))

    #
    # Main functions
    #
    def __determine_network_range(self) -> Dict[str, FourBytesLiteral]:

        ip = self.ip
        mask = self.mask

        # Network address
        net = FourBytesLiteral()
        for i in range(4):
            net.append(ip[i] & mask[i])

        # Broadcast address
        bct = FourBytesLiteral()
        for i in range(4):
            bct.append(ip[i] | (255 ^ mask[i]))

        result = {"start": net, "end": bct}
        self.network_range = result

        return result

    def __determine_type(self) -> int:
        """
        Determines the type of the given ip.

        :return:
            address_type: the address type of the machine
        :raises:
            IPOffNetworkRangeException: If the given IP is not in the network range
        """

        res = self.displayable_network_range

        if res['start'] == str(self.ip):
            self.address_type = 0
        elif res['end'] == str(self.ip):
            self.address_type = 2
        else:
            self.address_type = 1

        return self.address_type


class IPv4NetworkDisplayer(IPv4Network):

    def display_range(self, display=False) -> None:
        if display is True:
            self._display()
        else:
            print(Utils.netr_to_literal(self.network_range))

    def display_type(self, display=False) -> None:
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
