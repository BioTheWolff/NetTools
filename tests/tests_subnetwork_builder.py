import NetworkUtilities.core.subnetworkbuilder as sb
import unittest


class SubnetBuilderTests(unittest.TestCase):

    def test_subnet_sizes(self):
        inst = sb.SubnetworkBuilder('192.168.1.0', 18, [1500, 5000, 3680])
        expected_list = [
            {'start': '192.168.0.0', 'end': '192.168.31.255'},
            {'start': '192.168.32.0', 'end': '192.168.47.255'},
            {'start': '192.168.48.0', 'end': '192.168.55.255'}
        ]
        self.assertEqual(expected_list, inst.displayable_subnetworks)
