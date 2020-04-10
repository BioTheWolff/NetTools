import unittest
import NetworkUtilities.core.utils as u
import NetworkUtilities.core.errors as e


class UtilsTests(unittest.TestCase):
    c = u.Utils

    def test_ip_before_bottom_exception(self):
        self.assertRaises(e.IPv4LimitError, lambda: self.c.ip_before([0, 0, 0, 0]))

    def test_ip_before(self):
        self.assertEqual([192, 168, 1, 128], self.c.ip_before([192, 168, 1, 129]))
        self.assertEqual([192, 168, 0, 255], self.c.ip_before([192, 168, 1, 0]))
        self.assertEqual([192, 167, 255, 255], self.c.ip_before([192, 168, 0, 0]))
        self.assertEqual([191, 255, 255, 255], self.c.ip_before([192, 0, 0, 0]))

    def test_ip_after_top_exception(self):
        self.assertRaises(e.IPv4LimitError, lambda: self.c.ip_after([255, 255, 255, 255]))

    def test_ip_after(self):
        self.assertEqual([192, 168, 1, 129], self.c.ip_after([192, 168, 1, 128]))
        self.assertEqual([192, 168, 1, 0], self.c.ip_after([192, 168, 0, 255]))
        self.assertEqual([192, 168, 0, 0], self.c.ip_after([192, 167, 255, 255]))
        self.assertEqual([192, 0, 0, 0], self.c.ip_after([191, 255, 255, 255]))
