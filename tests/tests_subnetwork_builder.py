import NetworkUtilities.core.ipv4_network_compound as sb
import NetworkUtilities.utils.errors as e
import unittest
import unittest.mock as m


def init_cidr(sizes, cidr):
    return sb.IPv4NetworkCompound(sizes).init_from_cidr(cidr)


class SubnetBuilderTests(unittest.TestCase):

    def test_subnet_sizes(self):
        inst = init_cidr([1500, 5000, 3680], '192.168.1.0/18')
        expected_list = [
            {'start': '192.168.0.0', 'end': '192.168.31.255'},
            {'start': '192.168.32.0', 'end': '192.168.47.255'},
            {'start': '192.168.48.0', 'end': '192.168.55.255'}
        ]
        self.assertEqual(expected_list, inst.displayable_subnetworks)

    def test_exception_mask_too_small(self):
        self.assertRaises(e.MaskTooSmallException, lambda: init_cidr([200, 450], '192.168.1.4/24'))


class SubnetBuilderDisplays(unittest.TestCase):
    b = 'builtins.print'

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

        self.assertEqual([
            m.call("Network:"),
            m.call("CIDR : 192.168.1.0/18"),
            m.call("192.168.0.0 - 192.168.63.255"),
            m.call("16382 total addresses"),
            m.call(""),
            m.call("1 sub-network"),
            m.call("192.168.0.0 - 192.168.31.255 (8190 addresses)"),
        ], mocked_print.mock_calls)

    @m.patch(b)
    def test_print_fancy(self, mocked_print):
        init_cidr([1500, 5000, 3680], '192.168.1.0/18').print_subnetworks_fancy(False)

        self.assertEqual([
                m.call("Network:"),
                m.call("CIDR : 192.168.1.0/18"),
                m.call("192.168.0.0 - 192.168.63.255"),
                m.call("16382 total addresses"),
                m.call(""),
                m.call("3 sub-networks"),
                m.call("192.168.0.0 - 192.168.31.255 (8190 addresses)"),
                m.call("192.168.32.0 - 192.168.47.255 (4094 addresses)"),
                m.call("192.168.48.0 - 192.168.55.255 (2046 addresses)")
        ], mocked_print.mock_calls)

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
