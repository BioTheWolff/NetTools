import NetworkUtilities.core.network_basic as nb
import NetworkUtilities.core.errors as er
import unittest
import unittest.mock as mock


class NetworkBasicTests(unittest.TestCase):

    def _test_range(self, ip, mask=None):
        r = nb.NetworkBasic(ip, mask).determine_network_range()
        self.assertEqual({'start': '192.168.1.0', 'end': '192.168.1.255'}, r)

    def test_input_types(self):

        # CIDR
        self._test_range('192.168.1.0/24', None)

        # Mask length
        self._test_range('192.168.1.0', 24)

        # Mask literal
        self._test_range('192.168.1.0', '255.255.255.0')

        # Mask not provided Exception
        self.assertRaises(er.MaskNotProvided, lambda: self._test_range('192.168.1.0', None))

    #
    # RFC
    #
    def test_rfc_saved_types(self):

        # Class C network
        c = nb.NetworkBasic('192.168.0.0', 16).determine_network_range()
        self.assertEqual({'start': '192.168.0.0', 'end': '192.168.255.255'}, c)

        # Class B network
        b = nb.NetworkBasic('172.16.0.0', 12).determine_network_range()
        self.assertEqual({'start': '172.16.0.0', 'end': '172.31.255.255'}, b)

        # Class A network
        a = nb.NetworkBasic('10.0.0.0', 8).determine_network_range()
        self.assertEqual({'start': '10.0.0.0', 'end': '10.255.255.255'}, a)

    def test_rfc_going_out_allowed_range(self):

        # Class C going above 192.168.255.255 (would fall into 192.169.x.x which is public)
        self.assertRaises(er.NetworkLimitException, lambda: nb.NetworkBasic('192.168.255.128', 24)
                          .determine_network_range())

        # Class B going above 172.31.255.255 (would fall into 172.32.x.x which is public)
        self.assertRaises(er.NetworkLimitException, lambda: nb.NetworkBasic('172.31.255.128', 24)
                          .determine_network_range())

        # Class B going above 10.255.255.255 (would fall into 11.x.x.x which is public)
        self.assertRaises(er.NetworkLimitException, lambda: nb.NetworkBasic('10.255.255.128', 24)
                          .determine_network_range())

    def test_nfc_standards(self):
        # Wrong range
        self.assertRaises(er.RFCRulesIPWrongRangeException, lambda: nb.NetworkBasic('100.168.1.0', 24))

        # Wrong couples
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: nb.NetworkBasic('192.168.1.0', 15))
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: nb.NetworkBasic('172.16.1.0', 11))
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: nb.NetworkBasic('10.0.1.0', 7))

    #
    # Errors
    #
    def test_ip_errors(self):

        # Missing one IP byte
        self.assertRaises(er.IPBytesLengthException, lambda: self._test_range('192.168.1', 24))

        # Byte off range
        self.assertRaises(er.IPByteNumberOffLimitsException, lambda: self._test_range('192.168.999.1', 24))

    def test_mask_errors(self):

        # Length off bounds
        self.assertRaises(er.MaskLengthOffBoundsException, lambda: self._test_range('192.168.1.0', 33))

        # Wrong mask literal bytes length
        self.assertRaises(er.MaskBytesLengthException, lambda: self._test_range('192.168.1.0', '255.255.255'))

        # Mask byte off limits
        self.assertRaises(er.MaskByteNumberOffLimitsException, lambda: self._test_range('192.168.1.0', '255.255.0.999'))

        # Incorrect mask literal
        self.assertRaises(er.IncorrectMaskException, lambda: self._test_range('192.168.1.0', '255.255.195.0'))
        self.assertRaises(er.IncorrectMaskException, lambda: self._test_range('192.168.1.0', '255.255.254.255'))

    #
    # Network/Machine caracteristics
    #
    def test_addresses(self):
        a = nb.NetworkBasic('192.168.1.0', 24).addresses
        self.assertEqual(254, a)

    def test_machine_type(self):
        inst = nb.NetworkBasic('192.168.1.0', 24)

        # Network address
        self.assertEqual(inst.determine_type('192.168.1.0'), 0)

        # Computer address
        self.assertEqual(inst.determine_type('192.168.1.4'), 1)

        # Broadcast address
        self.assertEqual(inst.determine_type('192.168.1.255'), 2)

        # Errors: out of range
        err_inst = nb.NetworkBasic('192.168.1.128', 29)
        # before range
        self.assertRaises(er.IPOffNetworkRangeException, lambda: err_inst.determine_type('192.168.1.127'))

        # after range
        self.assertRaises(er.IPOffNetworkRangeException, lambda: err_inst.determine_type('192.168.1.127'))


class NetworkBasicDisplays(unittest.TestCase):

    #
    # Ranges display
    #
    @mock.patch('builtins.print')
    def test_display_range(self, mocked_print):
        nb.NetworkBasicDisplayer('192.168.1.0', 24).display_range()
        self.assertEqual([mock.call({'start': '192.168.1.0', 'end': '192.168.1.255'})], mocked_print.mock_calls)

    @mock.patch('builtins.print')
    def test_fancy_display_range(self, mocked_print):
        inst = nb.NetworkBasicDisplayer('192.168.1.0', 24)
        inst.display_range(display=True)

        expected_list = [
            mock.call("Network:"),
            mock.call(f"CIDR : {inst.ip}/{inst.mask_length}"),
            mock.call(f"{inst.network_range['start']} - {inst.network_range['end']}"),
            mock.call(f"{inst.addresses} available addresses")
        ]

        self.assertEqual(expected_list, mocked_print.mock_calls)

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
        inst = nb.NetworkBasicDisplayer('192.168.1.0', 24)
        inst.determine_network_range()

        inst.display_type(machine_ip, display=display)

        return inst

    @mock.patch('builtins.print')
    def test_fancy_type_network(self, mocked_print):
        # Network address
        inst = self._prepare_type_display('192.168.1.0')
        self.assertEqual([
            mock.call("Network:"),
            mock.call(f"CIDR : {inst.ip}/{inst.mask_length}"),
            mock.call(f"{inst.network_range['start']} - {inst.network_range['end']}"),
            mock.call(f"{inst.addresses} available addresses"),
            mock.call(''),
            mock.call("The address 192.168.1.0 is a network address")
        ], mocked_print.mock_calls, msg='Fancy display: network address')

    @mock.patch('builtins.print')
    def test_fancy_type_computer(self, mocked_print):
        # Computer address
        inst = self._prepare_type_display('192.168.1.4')
        self.assertEqual([
            mock.call("Network:"),
            mock.call(f"CIDR : {inst.ip}/{inst.mask_length}"),
            mock.call(f"{inst.network_range['start']} - {inst.network_range['end']}"),
            mock.call(f"{inst.addresses} available addresses"),
            mock.call(''),
            mock.call("The address 192.168.1.4 is a computer address")
        ], mocked_print.mock_calls, msg='Fancy display: computer address')

    @mock.patch('builtins.print')
    def test_fancy_type_broadcast(self, mocked_print):
        # Broadcast address
        inst = self._prepare_type_display('192.168.1.255')
        self.assertEqual([
            mock.call("Network:"),
            mock.call(f"CIDR : {inst.ip}/{inst.mask_length}"),
            mock.call(f"{inst.network_range['start']} - {inst.network_range['end']}"),
            mock.call(f"{inst.addresses} available addresses"),
            mock.call(''),
            mock.call("The address 192.168.1.255 is a broadcast address")
        ], mocked_print.mock_calls, msg='Fancy display: broadcast address')


class NetworkBasicForceCrash(unittest.TestCase):
    """
    Changing variables while we shouldnt so we provoke an Exception raise.
    Used for coverage.

    Keep in mind that these errors should never occur if one doesn't touch any variables.
    """

    @mock.patch('builtins.print')
    def test_unexpected_address_type(self, _):

        inst = nb.NetworkBasic('192.168.1.0', 24)
        inst.determine_type('192.168.1.5')

        # Force change type
        inst.address_type = 3

        # Force display call and fake parameters
        self.assertRaises(Exception, lambda: inst._display(machine_ip='192.168.1.5'))

    def test_wrong_rfc_current_range(self):

        # Create the range that won't be calculated, but is already known by the program because it is the 192.168/16
        # specified by RFC. Thus, it will be returned without calculus
        inst = nb.NetworkBasic('192.168.0.0', 16)

        # Force current range
        inst.rfc_current_range = 3

        # Try determining network range with wrong variable value
        self.assertRaises(Exception, lambda: inst.determine_network_range())
