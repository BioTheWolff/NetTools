from NetworkUtilities.utils.errors import MaskLengthOffBoundsException, \
    RFCRulesWrongCoupleException, \
    RFCRulesIPWrongRangeException, MaskNotProvided, IncorrectMaskException, BytesLengthException, \
    ByteNumberOffLimitsException
from NetworkUtilities.utils.utils import Utils
from NetworkUtilities.utils.ip_class import FourBytesLiteral
from typing import Union, Dict


class IPv4Network:
    __ip: FourBytesLiteral = None
    __mask: Union[FourBytesLiteral, str] = None
    __network_range: Dict[str, FourBytesLiteral] = {}

    __activated = False  # If IPv4Network has been initialized

    __address_type: int = None
    __mask_length, __addresses = 0, 0

    __rfc_current_range = None

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

    #
    # Read-only accesses properties
    #
    @property
    def ip(self):
        return self.__ip if self.__activated else None

    @property
    def mask(self):
        return self.__mask if self.__activated else None

    @property
    def mask_length(self):
        return self.__mask_length if self.__activated else None

    @property
    def network_range(self):
        return self.__network_range if self.__activated else None

    @property
    def addresses(self):
        return self.__addresses if self.__activated else None

    @property
    def address_type(self):
        return self.__address_type if self.__activated else None

    @property
    def activated(self):
        return self.__activated

    #
    # Displayable adaptation properties
    #
    @property
    def displayable_network_range(self):
        return Utils.netr_to_literal(self.__network_range)

    @property
    def displayable_address_type(self):
        li = [
            self.lang_dict['addr_types']['net'],
            self.lang_dict['addr_types']['mac'],
            self.lang_dict['addr_types']['bct']
        ]
        return li[self.__address_type]

    #
    # POSSIBLE INITS (built to chain)
    #
    def init_from_couple(self, ip: str, mask: Union[str, int]):
        self.__ip = FourBytesLiteral().set_from_string_literal(ip)
        self.__mask = mask

        # init "footer". All inits possess this footer to ensure both flow and instance returning
        self.__flow()
        return self

    def init_from_cidr(self, cidr: str):
        try:
            ip, mask = cidr.split('/')
            self.__ip = FourBytesLiteral().set_from_string_literal(ip)
            self.__mask = mask
        except ValueError:
            raise MaskNotProvided(cidr)

        self.__flow()
        return self

    def init_from_fbl(self, ip: FourBytesLiteral, mask: FourBytesLiteral):
        self.__ip = ip
        self.__mask = str(mask)

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

        self.__activated = True

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

        temp = self.__ip
        if len(temp) != 4:
            raise BytesLengthException('IP', len(temp))
        for e in temp:
            if not (0 <= int(e) <= 255):
                raise ByteNumberOffLimitsException('IP', e, temp.index(e))

        try:
            temp = self.__mask.split('.')
            if len(temp) == 1:
                raise AttributeError()
            if len(temp) != 4:
                raise BytesLengthException('mask', len(temp))
            for e in temp:
                if not (0 <= int(e) <= 255):
                    raise ByteNumberOffLimitsException('Mask', e, temp.index(e))
        except (AttributeError, ValueError):
            if 0 <= int(self.__mask) <= 32:
                return
            else:
                raise MaskLengthOffBoundsException(self.__mask)

    def __calculate_mask(self) -> None:
        """
        Calculates the mask from the instance var self.__mask

        If the mask is a literal mask (i.e. '255.255.255.0'), the try case is concerned.
        If instead, the user gave the mask length, we make sure to raise an AttributeError to switch to the
        except case to do proper testing.

        :raises:
            IncorrectMaskException: if the mask is wrongly formed (byte != 0 after byte < 255) or if the mask contains a
                byte that cannot be used in a mask.
        """

        try:
            # The mask is given by its literal
            temp = self.__mask.split('.')
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
            self.__mask_length = length
            self.__mask = FourBytesLiteral().set_from_string_literal(".".join(temp))

        except AttributeError:
            # The mask is given by its length
            self.__mask_length = int(self.__mask)
            self.__mask = FourBytesLiteral().set_from_string_literal(Utils.mask_length_to_literal(self.__mask_length))

        finally:
            self.__addresses = 2 ** (32 - self.__mask_length) - 2

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
                if (int(content[0]) == Utils.rfc_allowed_ranges[i_][0]) and \
                        (Utils.rfc_allowed_ranges[i_][1][0] <= int(content[1]) <= Utils.rfc_allowed_ranges[i_][1][1]):
                    ip_test = True
                    self.__rfc_current_range = i_

            if ip_test is False:
                raise RFCRulesIPWrongRangeException(ip[0], ip[1])

        ip = self.__ip
        mask = self.__mask_length

        # We check that ip respects RFC standards
        _check(ip)

        # We then check that provided mask corresponds to RFC standards
        for i in range(3):
            allowed = Utils.rfc_allowed_ranges[i][0]
            allowed_mask = Utils.rfc_masks[i]
            if (int(ip[0]) == allowed) and (mask < allowed_mask):
                raise RFCRulesWrongCoupleException(ip[0], ip[1], allowed_mask, mask)

    #
    # Template for child classes
    #
    def _display(self):
        literal_netr = self.displayable_network_range
        literal_ip = str(self.__ip)

        print(self.lang_dict['network'])
        print(self.lang_dict['cidr'].format(literal_ip, self.__mask_length))
        print("{} - {}".format(literal_netr['start'], literal_netr['end']))
        print(self.lang_dict['addr_avail'].format(self.__addresses))
        print('')

        self.__determine_type()
        if self.__address_type in [0, 1, 2]:
            types = ['net', 'mac', 'bct']
            machine_type = self.lang_dict['addr_types'][types[self.__address_type]]
        else:
            raise Exception("Given address type other than expected address types")

        print(self.lang_dict['addr_type'].format(literal_ip, machine_type))

    #
    # Main functions
    #
    def __determine_network_range(self) -> Dict[str, FourBytesLiteral]:

        ip = self.__ip
        mask = self.__mask

        # Network address
        net = FourBytesLiteral()
        for i in range(4):
            net.append(ip[i] & mask[i])

        # Broadcast address
        bct = FourBytesLiteral()
        for i in range(4):
            bct.append(ip[i] | (255 ^ mask[i]))

        result = {"start": net, "end": bct}
        self.__network_range = result

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

        if res['start'] == str(self.__ip):
            self.__address_type = 0
        elif res['end'] == str(self.__ip):
            self.__address_type = 2
        else:
            self.__address_type = 1

        return self.__address_type


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
