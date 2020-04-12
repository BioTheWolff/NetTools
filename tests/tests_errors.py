import unittest
import unittest.mock as m
import NetworkUtilities.utils.errors as e


class ErrorsInstanciationTests(unittest.TestCase):
    b = 'builtins.print'

    @m.patch(b)
    def test_bytes_length_exception(self, mocked_print):
        inst = e.BytesLengthException('IP', 5)
        print(str(inst))

        self.assertEqual([m.call('IP must be 4 bytes long, found 5 byte(s).')],
                         mocked_print.mock_calls)

    @m.patch(b)
    def test_byte_number_off_limits_exception(self, mocked_print):
        inst = e.ByteNumberOffLimitsException('IP', 399, 2)
        print(str(inst))

        self.assertEqual([m.call('IP bytes must be between 0 and 255. Found 399 at byte 2')],
                         mocked_print.mock_calls)

    @m.patch(b)
    def test_ip_off_network_range_exception(self, mocked_print):
        inst = e.IPOffNetworkRangeException('192.168.1.0')
        print(str(inst))

        self.assertEqual([m.call("IP address 192.168.1.0 not in network range.")], mocked_print.mock_calls)

    @m.patch(b)
    def test_mask_not_provided_exception(self, mocked_print):
        inst = e.MaskNotProvided('192.168.1.0')
        print(str(inst))

        self.assertEqual([m.call("Could not find IP and mask in given cidr 192.168.1.0")], mocked_print.mock_calls)

    @m.patch(b)
    def test_mask_off_bounds_exception(self, mocked_print):
        inst = e.MaskLengthOffBoundsException(35)
        print(str(inst))

        self.assertEqual([m.call("Provided mask length (35) out of bounds [0-32]")], mocked_print.mock_calls)

    @m.patch(b)
    def test_incorrect_mask_exception_1(self, mocked_print):
        inst = e.IncorrectMaskException(True, 35)
        print(str(inst))

        self.assertEqual([m.call("Incorrect mask. Allowed values are [0,128,192,224,240,248,242,254,255], "
                                 "found 35")], mocked_print.mock_calls)

    @m.patch(b)
    def test_incorrect_mask_exception_2(self, mocked_print):
        inst = e.IncorrectMaskException(False, 35, 3)
        print(str(inst))

        self.assertEqual([m.call("Mask bytes must all be empty (0) after a byte with a value under 255, found "
                                 "35 at byte 3")], mocked_print.mock_calls)

    @m.patch(b)
    def test_mask_too_small_exception(self, mocked_print):
        inst = e.MaskTooSmallException(16, 14)
        print(str(inst))

        self.assertEqual([m.call("Given mask length (16) cannot handle all the addresses of the subnetworks. "
                                 "Advised length : 14")], mocked_print.mock_calls)

    @m.patch(b)
    def test_rfc_ip_wrong_range_exception(self, mocked_print):
        inst = e.RFCRulesIPWrongRangeException(16, 14)
        print(str(inst))

        self.assertEqual([m.call("IP must be either 192.168.x.x , 172.16.x.x or 10.0.x.x; found 16.14.x.x"
                                 )], mocked_print.mock_calls)

    @m.patch(b)
    def test_rfc_wrong_couple_exception(self, mocked_print):
        inst = e.RFCRulesWrongCoupleException(16, 14, 20, 17)
        print(str(inst))

        self.assertEqual([m.call("According to RFC standards, given couple must be 16.14.x.x/>=20, "
                                 "found mask length 17")], mocked_print.mock_calls)

    @m.patch(b)
    def test_network_limit_exception(self, mocked_print):
        inst = e.NetworkLimitException()
        print(str(inst))

        self.assertEqual([m.call("RFC range limit reached while trying to determine network range.")],
                         mocked_print.mock_calls)

    @m.patch(b)
    def test_ipv4_limit_exception_1(self, mocked_print):
        inst = e.IPv4LimitError("bottom")
        print(str(inst))

        self.assertEqual([m.call("IPv4 bottom limit (0.0.0.0) reached")],
                         mocked_print.mock_calls)

    @m.patch(b)
    def test_ipv4_limit_exception_2(self, mocked_print):
        inst = e.IPv4LimitError("top")
        print(str(inst))

        self.assertEqual([m.call("IPv4 top limit (255.255.255.255) reached")],
                         mocked_print.mock_calls)
