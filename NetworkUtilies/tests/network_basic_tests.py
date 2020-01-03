import NetworkUtilies.core.network_basic as nb
import NetworkUtilies.core.errors as er


class TestBasicClass:

    def test_range(self):
        r = nb.NetworkBasic('192.168.1.0', 24).determine_network_range()
        assert {'start': '192.168.1.0', 'end': '192.168.1.255'} == r

    def test_addresses(self):
        a = nb.NetworkBasic('192.168.1.0', 24).addresses
        assert a == 254

    def test_machine_type(self):
        inst = nb.NetworkBasic('192.168.1.0', 24)

        # Network address
        assert inst.determine_type('192.168.1.0') == 0

        # Computer address
        assert inst.determine_type('192.168.1.225') == 1

        # Broadcast address
        assert inst.determine_type('192.168.1.255') == 2

        # Errors: out of range
        err_inst = nb.NetworkBasic('192.168.1.128', 29)
        # before range
        try:
            err_inst.determine_type('192.168.1.127')
        except er.IPOffNetworkRangeException:
            pass

        # after range
        try:
            err_inst.determine_type('192.168.1.136')
        except er.IPOffNetworkRangeException:
            pass

    def test_nfc_standards(self):
        # Wrong range
        try:
            _ = nb.NetworkBasic('100.168.1.0', 24)
        except er.RFCRulesIPWrongRangeException:
            pass

        # Wrong couples
        try:
            _ = nb.NetworkBasic('192.168.1.0', 15)
        except er.RFCRulesWrongCoupleException:
            pass

        try:
            _ = nb.NetworkBasic('172.16.1.0', 11)
        except er.RFCRulesWrongCoupleException:
            pass

        try:
            _ = nb.NetworkBasic('10.0.1.0', 7)
        except er.RFCRulesWrongCoupleException:
            pass
