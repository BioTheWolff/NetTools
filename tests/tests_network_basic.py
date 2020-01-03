import NetworkUtilities.core.network_basic as nb
import NetworkUtilities.core.errors as er
import unittest


class NetworkBasicTests(unittest.TestCase):

    def test_range(self):
        r = nb.NetworkBasic('192.168.1.0', 24).determine_network_range()
        self.assertEqual({'start': '192.168.1.0', 'end': '192.168.1.255'}, r)

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
