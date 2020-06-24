import unittest
import unittest.mock as m
from nettools import *


def init_cidr(sizes, cidr):
    return IPv4NetworkCompound().init_from_cidr(cidr).add_from_addresses(sizes)


class IPv4NetworkCompoundTests(unittest.TestCase):

    def test_inits(self):
        ip = FourBytesLiteral().set_from_string_literal('192.168.1.0')
        mask = FourBytesLiteral().set_from_string_literal('255.255.254.0')
        expected = [
            {'start': '192.168.0.0', "end": '192.168.0.255'}
        ]

        test1 = IPv4NetworkCompound().init_from_fbl(ip, mask).add_from_addresses(250)
        test2 = IPv4NetworkCompound().init_from_couple(str(ip), str(mask)).add_from_addresses(250)

        self.assertEqual(expected, test1.displayable_subnetworks)
        self.assertEqual(expected, test2.displayable_subnetworks)

    def test_subnet_sizes(self):
        inst = init_cidr([1500, 5000, 3680], '192.168.1.0/18')
        expected_list = [
            {'start': '192.168.0.0', 'end': '192.168.31.255'},
            {'start': '192.168.32.0', 'end': '192.168.47.255'},
            {'start': '192.168.48.0', 'end': '192.168.55.255'}
        ]
        self.assertEqual(expected_list, inst.displayable_subnetworks)

    def test_exception_mask_too_small(self):
        self.assertRaises(MaskTooSmallException, lambda: init_cidr([200, 450], '192.168.1.4/24'))

    def test_insertion_list(self):
        test = init_cidr([250, 250], '192.168.0.0/18')
        expected = [
            {'start': '192.168.0.0', "end": '192.168.0.255'},
            {'start': '192.168.1.0', "end": '192.168.1.255'}
        ]

        self.assertEqual(expected, test.displayable_subnetworks)

    def test_insertion_int(self):
        test = init_cidr(250, '192.168.0.0/18')
        test.add_from_addresses(250)
        expected = [
            {'start': '192.168.0.0', "end": '192.168.0.255'},
            {'start': '192.168.1.0', "end": '192.168.1.255'}
        ]

        self.assertEqual(expected, test.displayable_subnetworks)

    def test_deleting_subnet(self):
        test = init_cidr([250, 250], '192.168.0.0/18')
        test.remove_subnet(0)
        expected = [
            {'start': '192.168.1.0', "end": '192.168.1.255'}
        ]

        self.assertEqual(expected, test.displayable_subnetworks)

    def test_property_activated(self):
        test = IPv4NetworkCompound().init_from_cidr('192.168.1.0/23')
        self.assertEqual(False, test.activated)

        test.add_from_addresses([250])
        self.assertEqual(True, test.activated)

    def test_property_subnets(self):
        test = IPv4NetworkCompound().init_from_cidr('192.168.1.0/24')
        self.assertEqual(None, test.subnets)


class IPv4NetworkCompoundDisplays(unittest.TestCase):
    b = 'builtins.print'

    @staticmethod
    def fill_mock_calls(subnet_num, other=None):
        s = 's' if subnet_num > 1 else ''
        li = [
            m.call("Network:"),
            m.call("CIDR : 192.168.1.0/18"),
            m.call("192.168.0.0 - 192.168.63.255"),
            m.call("16382 total addresses"),
            m.call(""),
            m.call(f"{subnet_num} sub-network{s}"),
            m.call("192.168.0.0 - 192.168.31.255 (8190 addresses)"),
        ]

        if other is not None:
            li.extend(other)

        return li

    @m.patch(b)
    def test_print(self, mocked_print):
        init_cidr([1500, 5000, 3680], '192.168.1.0/18').print_subnetworks()

        self.assertEqual([m.call([{'start': '192.168.0.0', 'end': '192.168.31.255'},
                                 {'start': '192.168.32.0', 'end': '192.168.47.255'},
                                 {'start': '192.168.48.0', 'end': '192.168.55.255'}])],
                         mocked_print.mock_calls)

    @m.patch(b)
    def test_print_fancy_only_one_subnet(self, mocked_print):
        init_cidr([5000], '192.168.1.0/18').print_subnetworks_fancy(False)

        self.assertEqual(self.fill_mock_calls(1), mocked_print.mock_calls)

    @m.patch(b)
    def test_print_fancy(self, mocked_print):
        init_cidr([1500, 5000, 3680], '192.168.1.0/18').print_subnetworks_fancy(False)

        self.assertEqual(self.fill_mock_calls(3, [
                m.call("192.168.32.0 - 192.168.47.255 (4094 addresses)"),
                m.call("192.168.48.0 - 192.168.55.255 (2046 addresses)")
        ]), mocked_print.mock_calls)

    @m.patch(b)
    def test_print_fancy_advanced(self, mocked_print):
        init_cidr([1500, 5000, 3680], '192.168.1.0/18').print_subnetworks_fancy(True)

        self.assertEqual([
            m.call("Network:"),
            m.call("CIDR (Classless Inter Domain Routing) : 192.168.1.0/18"),
            m.call("192.168.0.0 - 192.168.63.255"),
            m.call("addresses: 14330 occupied / 16382 total"),
            m.call(""),
            m.call("3 sub-networks"),
            m.call("192.168.0.0 - 192.168.31.255 (8190 available addresses, 5000 requested)"),
            m.call("192.168.32.0 - 192.168.47.255 (4094 available addresses, 3680 requested)"),
            m.call("192.168.48.0 - 192.168.55.255 (2046 available addresses, 1500 requested)"),
            m.call(""),
            m.call("Network usage:"),
            m.call("[██████████████████░░] 87 %")
        ], mocked_print.mock_calls)
