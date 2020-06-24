import unittest
from nettools import FourBytesLiteral, LimitedList


class FBLTests(unittest.TestCase):

    @staticmethod
    def inst_fbl():
        return FourBytesLiteral().set_eval('192.168.1.0')

    def test_get_bytes_content(self):
        self.assertEqual([192, 168, 1, 0], self.inst_fbl().bytes_list)

    # Dunders
    def test_get_item(self):
        self.assertEqual(192, self.inst_fbl()[0])

    def test_set_item(self):
        test = self.inst_fbl()
        test[1] = 100

        self.assertEqual([192, 100, 1, 0], test.bytes_list)

    def test_index(self):
        self.assertEqual(1, self.inst_fbl().index(168))

    # Exceptions
    def test_exception_eval_not_recognised(self):
        self.assertRaises(Exception, lambda: self.inst_fbl().set_eval({"test": "test"}))

    def test_exception_limited_list_too_big(self):
        li = LimitedList(5)
        self.assertRaises(Exception, lambda: FourBytesLiteral().set_eval(li))

    def test_exception_builtin_list_too_big(self):
        self.assertRaises(Exception, lambda: FourBytesLiteral().set_eval([192, 168, 1, 0, 5]))

    # Partial filling
    def test_partial_fill_limited_list(self):
        li = LimitedList(4).append_all([192, 168])
        inst = FourBytesLiteral().set_eval(li)

        self.assertEqual([192, 168, 0, 0], inst.bytes_list)

    def test_partial_fill_builtin_list(self):
        inst = FourBytesLiteral().set_eval([192, 168])

        self.assertEqual([192, 168, 0, 0], inst.bytes_list)


class LLTests(unittest.TestCase):

    def test_exception_overflow_append(self):
        inst = LimitedList(2).append_all([1, 2])
        self.assertRaises(OverflowError, lambda: inst.append(3))

    def test_exception_overflow_append_all(self):
        inst = LimitedList(2)
        self.assertRaises(OverflowError, lambda: inst.append_all([1, 2, 3, 4]))


if __name__ == '__main__':
    unittest.main()
