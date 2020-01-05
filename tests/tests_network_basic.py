import NetworkUtilities.core.network_basic as nb
import NetworkUtilities.core.errors as er
import unittest


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

    def test_addresses(self):
        a = nb.NetworkBasic('192.168.1.0', 24).addresses
        self.assertEqual(254, a)

    def test_machine_type(self):
        inst = nb.NetworkBasic('192.168.1.0', 24)

        # Network address
        self.assertEqual(inst.determine_type('192.168.1.0'), 0)

        # Computer address
        self.assertEqual(inst.determine_type('192.168.1.225'), 1)

        # Broadcast address
        self.assertEqual(inst.determine_type('192.168.1.255'), 2)

        # Errors: out of range
        err_inst = nb.NetworkBasic('192.168.1.128', 29)
        # before range
        self.assertRaises(er.IPOffNetworkRangeException, lambda: err_inst.determine_type('192.168.1.127'))

        # after range
        self.assertRaises(er.IPOffNetworkRangeException, lambda: err_inst.determine_type('192.168.1.127'))

    def test_nfc_standards(self):
        # Wrong range
        self.assertRaises(er.RFCRulesIPWrongRangeException, lambda: nb.NetworkBasic('100.168.1.0', 24))

        # Wrong couples
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: nb.NetworkBasic('192.168.1.0', 15))
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: nb.NetworkBasic('172.16.1.0', 11))
        self.assertRaises(er.RFCRulesWrongCoupleException, lambda: nb.NetworkBasic('10.0.1.0', 7))
