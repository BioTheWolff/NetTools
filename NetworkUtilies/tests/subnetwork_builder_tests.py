import NetworkUtilies.utils.subnetworkbuilder as sb


class SubnetBuilderTestClass:

    def test_subnet_sizes(self):
        inst = sb.SubnetworkBuilder('192.168.1.0', 18, [1500, 5000, 3680])
        expected_list = [
            {'start': '192.168.1.0', 'end': '192.168.32.255'},
            {'start': '192.168.33.0', 'end': '192.168.48.255'},
            {'start': '192.168.49.0', 'end': '192.168.56.255'}
        ]
        assert inst.build_subnets(returning=True) == expected_list
