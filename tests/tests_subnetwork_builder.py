import NetworkUtilities.utils.subnetworkbuilder as sb
import unittest


class SubnetBuilderTests(unittest.TestCase):

    def test_subnet_sizes(self):
        inst = sb.SubnetworkBuilder('192.168.1.0', 18, [1500, 5000, 3680])
        expected_list = [
            {'start': '192.168.1.0', 'end': '192.168.32.255'},
            {'start': '192.168.33.0', 'end': '192.168.48.255'},
            {'start': '192.168.49.0', 'end': '192.168.56.255'}
        ]
        self.assertEqual(expected_list, inst.build_subnets(returning=True))
