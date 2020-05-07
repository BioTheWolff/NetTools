import NetworkUtilities.core.network_basic as nb
import NetworkUtilities.utils.errors as er
import unittest
import unittest.mock as mock


def init_couple(i, m):
    return nb.IPv4Network().init_from_couple(i, m)


def init_cidr(c):
    return nb.IPv4Network().init_from_cidr(c)


class IPv4NetworkTests(unittest.TestCase):

    def _test_range(self, ip, mask=None):
        r = init_couple(ip, mask).displayable_network_range
        self.assertEqual({'start': '192.168.1.0', 'end': '192.168.1.255'}, r)

    def test_input_types(self):

        # CIDR
        init_cidr('192.168.1.0/24')

        # Mask length
        self._test_range('192.168.1.0', 24)

        # Mask literal
        self._test_range('192.168.1.0', '255.255.255.0')

        # Mask not provided Exception
        self.assertRaises(er.MaskNotProvided, lambda: init_cidr('192.168.1.0'))

    @staticmethod
    def test_trying_masks_literals():

        masks = [
            # Class A and less
            '255.0.0.0',
            '255.128.0.0',
            '255.192.0.0',
            '255.224.0.0',
            '255.240.0.0',
            '255.248.0.0',
            '255.252.0.0',
            '255.254.0.0',
            # Class B and less
            '255.255.0.0',
            '255.255.128.0',
            '255.255.192.0',
            '255.255.224.0',
            '255.255.240.0',
            '255.255.248.0',
            '255.255.252.0',
            '255.255.254.0',
            # Class C and less
            '255.255.255.0',
            '255.255.255.128',
            '255.255.255.192',
            '255.255.255.224',
            '255.255.255.240',
            '255.255.255.248',
            '255.255.255.252',
            '255.255.255.254'
        ]

        for mask in masks:
            init_couple('10.0.0.0', mask)

    @staticmethod
    def test_trying_masks_lengths():

        for i in range(8, 32):
            nb.IPv4Network().init_from_couple('10.0.0.0', i)

    #
    # RFC
    #
    def test_rfc_standards(self):
        # Wrong range
        self.assertRaises(er.RFCRulesIPWrongRangeException, lambda: init_couple('100.168.1.0', 24))

        # Wrong couples
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: init_couple('192.168.1.0', 15))
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: init_couple('172.16.1.0', 11))
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: init_couple('10.0.1.0', 7))

    #
    # Errors
    #
    def test_ip_errors(self):

        # Missing one IP byte
        self.assertRaises(er.BytesLengthException, lambda: self._test_range('192.168.1', 24))

        # Byte off range
        self.assertRaises(er.ByteNumberOffLimitsException, lambda: self._test_range('192.168.999.1', 24))

    def test_mask_errors(self):

        # Length off bounds
        self.assertRaises(er.MaskLengthOffBoundsException, lambda: self._test_range('192.168.1.0', 33))

        # Wrong mask literal bytes length
        self.assertRaises(er.BytesLengthException, lambda: self._test_range('192.168.1.0', '255.255.255'))

        # Mask byte off limits
        self.assertRaises(er.ByteNumberOffLimitsException, lambda: self._test_range('192.168.1.0', '255.255.0.999'))

        # Incorrect mask literals:
        # Byte not allowed
        self.assertRaises(er.IncorrectMaskException, lambda: self._test_range('192.168.1.0', '255.255.195.0'))
        # Non-empty byte after byte < 255
        self.assertRaises(er.IncorrectMaskException, lambda: self._test_range('192.168.1.0', '255.255.254.255'))

    #
    # Network/Machine caracteristics
    #
    def test_addresses(self):
        a = init_couple('192.168.1.0', 24).addresses
        self.assertEqual(254, a)

    def test_machine_type(self):

        # Network address
        self.assertEqual(init_couple('192.168.1.0', 24).displayable_address_type, "network")

        # Computer address
        self.assertEqual(init_couple('192.168.1.4', 24).displayable_address_type, "computer")

        # Broadcast address
        self.assertEqual(init_couple('192.168.1.255', 24).displayable_address_type, "broadcast")


class IPv4NetworkDisplays(unittest.TestCase):

    #
    # Ranges display
    #
    @mock.patch('builtins.print')
    def test_display_range(self, mocked_print):
        nb.IPv4NetworkDisplayer().init_from_couple('192.168.1.0', 24).display_range()
        self.assertEqual([mock.call({'start': '192.168.1.0', 'end': '192.168.1.255'})], mocked_print.mock_calls)

    #
    # Normal types displays
    #
    @mock.patch('builtins.print')
    def test_type_network(self, mocked_print):
        # Network address
        self._prepare_type_display('192.168.1.0', display=False)
        self.assertEqual([
            mock.call({'start': '192.168.1.0', 'end': '192.168.1.255', 'address_type': 'network'})
        ], mocked_print.mock_calls, msg='Normal display: network address')

    @mock.patch('builtins.print')
    def test_type_computer(self, mocked_print):
        # Computer address
        self._prepare_type_display('192.168.1.4', display=False)
        self.assertEqual([
            mock.call({'start': '192.168.1.0', 'end': '192.168.1.255', 'address_type': 'computer'})
        ], mocked_print.mock_calls, msg='Normal display: computer address')

    @mock.patch('builtins.print')
    def test_type_broadcast(self, mocked_print):
        # Broadcast address
        self._prepare_type_display('192.168.1.255', display=False)
        self.assertEqual([
            mock.call({'start': '192.168.1.0', 'end': '192.168.1.255', 'address_type': 'broadcast'})
        ], mocked_print.mock_calls, msg='Normal display: broadcast address')

    #
    # Fancy types displays
    #
    @staticmethod
    def _prepare_type_display(machine_ip, display=True):
        inst = nb.IPv4NetworkDisplayer().init_from_couple(machine_ip, 24)
        inst.display_type(display=display)

        return inst

    @mock.patch('builtins.print')
    def test_fancy_type_network(self, mocked_print):
        # Network address
        self._prepare_type_display('192.168.1.0')
        self.assertEqual([
            mock.call("Network:"),
            mock.call("CIDR : 192.168.1.0/24"),
            mock.call("192.168.1.0 - 192.168.1.255"),
            mock.call("254 total addresses"),
            mock.call(''),
            mock.call("The address 192.168.1.0 is a network address")
        ], mocked_print.mock_calls, msg='Fancy display: network address')

    @mock.patch('builtins.print')
    def test_fancy_type_computer(self, mocked_print):
        # Computer address
        self._prepare_type_display('192.168.1.4')
        self.assertEqual([
            mock.call("Network:"),
            mock.call("CIDR : 192.168.1.4/24"),
            mock.call("192.168.1.0 - 192.168.1.255"),
            mock.call("254 total addresses"),
            mock.call(''),
            mock.call("The address 192.168.1.4 is a computer address")
        ], mocked_print.mock_calls, msg='Fancy display: computer address')

    @mock.patch('builtins.print')
    def test_fancy_type_broadcast(self, mocked_print):
        # Broadcast address
        self._prepare_type_display('192.168.1.255')
        self.assertEqual([
            mock.call("Network:"),
            mock.call("CIDR : 192.168.1.255/24"),
            mock.call("192.168.1.0 - 192.168.1.255"),
            mock.call("254 total addresses"),
            mock.call(''),
            mock.call("The address 192.168.1.255 is a broadcast address")
        ], mocked_print.mock_calls, msg='Fancy display: broadcast address')
