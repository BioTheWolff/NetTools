from NetworkUtilities.core.ipv4_network import IPv4Network
from NetworkUtilities.utils.errors import MaskTooSmallException
from NetworkUtilities.utils.utils import Utils
from NetworkUtilities.utils.ip_class import FourBytesLiteral
from typing import Union, List


class IPv4NetworkCompound(IPv4Network):
    total_network_range = None

    subnets_sizes: List[int] = None
    subnets: List[IPv4Network] = None
    submasks_machine_bits: List[int] = None

    def __build_graph(self):
        # graph
        occupied = 0
        for i in range(len(self.submasks_machine_bits)):
            occupied += 2 ** self.submasks_machine_bits[i] - 2
        percentage = round((occupied / self.addresses) * 100)
        graph = '['
        current = 0
        for i in range(20):
            if current < percentage:
                graph += '█'
            else:
                graph += '░'
            current += 5
        graph += "] {} %".format(percentage)

        if len(self.subnets) > 1:
            t = 's'
        else:
            t = ''

        return occupied, graph, t

    def __display_subnets(self, advanced=False) -> None:

        occupied, graph, t = self.__build_graph()

        literal_ip = Utils.to_literal(self.ip)
        literal_netr = Utils.netr_to_literal(self.total_network_range)

        print(self.lang_dict['network'])
        if advanced is True:
            print(self.lang_dict['cidr_adv'].format(literal_ip, self.mask_length))
        else:
            print(self.lang_dict['cidr'].format(literal_ip, self.mask_length))
        print("{} - {}".format(literal_netr['start'], literal_netr['end']))
        if advanced is True:
            print(self.lang_dict['addr_avail_advanced'].format(occupied, self.addresses))
        else:
            print(self.lang_dict['addr_avail'].format(self.addresses))
        print('')
        print(self.lang_dict['utils'].format(len(self.subnets), t))

        for i in range(len(self.subnets)):
            literal_sub_netr = self.subnets[i].displayable_network_range

            if advanced:
                print(self.lang_dict['sub_addr_advanced'].format(literal_sub_netr['start'],
                                                                 literal_sub_netr['end'],
                                                                 2 ** self.submasks_machine_bits[i] - 2,
                                                                 self.subnets_sizes[i]))
            else:
                print(self.lang_dict['sub_addr'].format(literal_sub_netr['start'],
                                                        literal_sub_netr['end'],
                                                        2 ** self.submasks_machine_bits[i] - 2))

        if advanced:
            print('')
            print(self.lang_dict['net_usage'])
            print(graph)

    def __to_printable_subnets(self):
        return [n.displayable_network_range for n in self.subnets]

    def __determine_required_submasks_sizes(self) -> None:

        submasks = []

        for i in range(len(self.subnets_sizes)):
            power = 1
            while 2 ** power - 2 < self.subnets_sizes[i]:
                power += 1
            submasks.append(power)

        self.submasks_machine_bits = submasks

    #
    # Init
    #

    def init_from_couple(self, ip: str, mask: Union[str, int]):
        super().init_from_couple(ip, mask)
        return self

    def init_from_cidr(self, cidr: str):
        super().init_from_cidr(cidr)
        return self

    def init_from_fbl(self, ip: FourBytesLiteral, mask: FourBytesLiteral):
        super().init_from_fbl(ip, mask)
        return self

    #
    # Fill compound
    #
    def add_from_addresses(self, sizes: Union[List, int]):
        if isinstance(sizes, int):
            sizes = [sizes]

        if not self.subnets_sizes:
            self.subnets_sizes = sorted(sizes, reverse=True)
        else:
            li = self.subnets_sizes
            li.extend(sizes)
            self.subnets_sizes = sorted(li, reverse=True)

        self.__subnet_flow()
        return self

    #
    # Flow
    #
    def __subnet_flow(self):
        self.subnets = []
        self.submasks_machine_bits = []

        # first, let's check if the provided mask can handle all the addresses requested
        self.total_network_range = self.displayable_network_range
        self.__determine_required_submasks_sizes()

        total = 0

        for i in range(len(self.submasks_machine_bits)):
            total += 2 ** self.submasks_machine_bits[i]

        if self.addresses < total:
            power = 1
            while total > 2 ** power:
                power += 1
            raise MaskTooSmallException(self.mask_length, 32 - power)

        self.__build_subnets()

    def __build_subnets(self) -> None:
        start_ip = self.network_range['start']

        for i in range(len(self.subnets_sizes)):
            machines_bits = self.submasks_machine_bits[i]
            mask_literal = FourBytesLiteral().set_eval(Utils.mask_length_to_literal(32 - machines_bits))

            result = IPv4Network().init_from_fbl(start_ip, mask_literal)
            self.subnets.append(result)
            start_ip = Utils.ip_after(result.network_range['end'])

    @staticmethod
    def __determine_subnet_range(ip: FourBytesLiteral = None, machine_bits: int = None):

        mask = [int(i) for i in
                Utils.mask_length_to_literal(32 - machine_bits).split('.')
                ]

        net = FourBytesLiteral()
        for i in range(4):
            net.append(ip[i] & mask[i])

        # Broadcast address
        bct = FourBytesLiteral()
        for i in range(4):
            bct.append(ip[i] | (255 ^ mask[i]))

        return {"start": net, "end": bct}

    #
    # Displays
    #
    @property
    def displayable_subnetworks(self):
        return self.__to_printable_subnets()

    def print_subnetworks(self):
        print(self.__to_printable_subnets())

    def print_subnetworks_fancy(self, advanced=False):
        self.__display_subnets(advanced)
