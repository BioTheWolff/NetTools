import unittest
from nettools import *


def content(x, tweak=None):
    if tweak is None:
        return FourBytesLiteral().set_eval(x).bytes.content
    elif tweak is False:
        return Utils.ip_before(FourBytesLiteral().set_eval(x)).bytes.content
    elif tweak is True:
        return Utils.ip_after(FourBytesLiteral().set_eval(x)).bytes.content


class UtilsTests(unittest.TestCase):
    c = Utils

    def test_ip_before_bottom_exception(self):
        self.assertRaises(IPv4LimitError, lambda: content([0, 0, 0, 0], False))

    def test_ip_before(self):
        self.assertEqual(content([192, 168, 1, 128]), content([192, 168, 1, 129], False))
        self.assertEqual(content([192, 168, 0, 255]), content([192, 168, 1, 0], False))
        self.assertEqual(content([192, 167, 255, 255]), content([192, 168, 0, 0], False))
        self.assertEqual(content([191, 255, 255, 255]), content([192, 0, 0, 0], False))

    def test_ip_after_top_exception(self):
        self.assertRaises(IPv4LimitError, lambda: content([255, 255, 255, 255], True))

    def test_ip_after(self):
        self.assertEqual(content([192, 168, 1, 129]), content([192, 168, 1, 128], True))
        self.assertEqual(content([192, 168, 1, 0]), content([192, 168, 0, 255], True))
        self.assertEqual(content([192, 168, 0, 0]), content([192, 167, 255, 255], True))
        self.assertEqual(content([192, 0, 0, 0]), content([191, 255, 255, 255], True))

    def test_dec_to_bin(self):
        self.assertEqual(110100, self.c.dec_to_bin(52))

    def test_ip_in_range(self):
        netr = {
            "start": FourBytesLiteral().set_eval('192.168.1.0'),
            "end": FourBytesLiteral().set_eval('192.168.1.255')
        }

        in_r = FourBytesLiteral().set_eval('192.168.1.4')
        out_r = FourBytesLiteral().set_eval('192.168.4.0')

        self.assertEqual(True, self.c.ip_in_range(netr, in_r), msg="In range")
        self.assertEqual(False, self.c.ip_in_range(netr, out_r), msg="Not in range")
