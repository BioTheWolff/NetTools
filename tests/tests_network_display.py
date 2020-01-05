import unittest
import unittest.mock as mock
import NetworkUtilities.core.network_basic as nb


class MyTestCase(unittest.TestCase):

    @mock.patch('builtins.print')
    def test_display_range(self, mocked_print):
        nb.NetworkBasicDisplayer('192.168.1.0', 24).display_range()
        self.assertEqual([mock.call({'start': '192.168.1.0', 'end': '192.168.1.255'})], mocked_print.mock_calls)

    @mock.patch('builtins.print')
    def test_display_range_fancy(self, mocked_print):
        nb.NetworkBasicDisplayer('192.168.1.0', 24).display_range(display=True)
        assert True is False


if __name__ == '__main__':
    unittest.main()
