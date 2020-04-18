import unittest
import NetworkUtilities.utils.utils as u
import NetworkUtilities.utils.errors as e
import NetworkUtilities.utils.ip_class as i


def content(x, tweak=None):
    if tweak is None:
        return i.FourBytesLiteral().set_eval(x).bytes.content
    elif tweak is False:
        return u.Utils.ip_before(i.FourBytesLiteral().set_eval(x)).bytes.content
    elif tweak is True:
        return u.Utils.ip_after(i.FourBytesLiteral().set_eval(x)).bytes.content


class UtilsTests(unittest.TestCase):
    c = u.Utils

    def test_ip_before_bottom_exception(self):
        self.assertRaises(e.IPv4LimitError, lambda: content([0, 0, 0, 0], False))

    def test_ip_before(self):
        self.assertEqual(content([192, 168, 1, 128]), content([192, 168, 1, 129], False))
        self.assertEqual(content([192, 168, 0, 255]), content([192, 168, 1, 0], False))
        self.assertEqual(content([192, 167, 255, 255]), content([192, 168, 0, 0], False))
        self.assertEqual(content([191, 255, 255, 255]), content([192, 0, 0, 0], False))

    def test_ip_after_top_exception(self):
        self.assertRaises(e.IPv4LimitError, lambda: content([255, 255, 255, 255], True))

    def test_ip_after(self):
        self.assertEqual(content([192, 168, 1, 129]), content([192, 168, 1, 128], True))
        self.assertEqual(content([192, 168, 1, 0]), content([192, 168, 0, 255], True))
        self.assertEqual(content([192, 168, 0, 0]), content([192, 167, 255, 255], True))
        self.assertEqual(content([192, 0, 0, 0]), content([191, 255, 255, 255], True))