import unittest

from plot_likert.interval import *


class TestIntervalCalculations(unittest.TestCase):
    def test_get_next_interval_divisor(self):
        generator = get_next_interval_divisor()
        divisor = generator.__next__()
        self.assertEqual(5, divisor)
        divisor = generator.__next__()
        self.assertEqual(10, divisor)
        divisor = generator.__next__()
        self.assertEqual(100, divisor)
        divisor = generator.__next__()
        self.assertEqual(1000, divisor)

    def test_get_biggest_divisor(self):
        self.assertEqual(1, get_biggest_divisor(4))
        self.assertEqual(5, get_biggest_divisor(5))
        self.assertEqual(1, get_biggest_divisor(9))
        self.assertEqual(10, get_biggest_divisor(10))
        self.assertEqual(5, get_biggest_divisor(15))
        self.assertEqual(100, get_biggest_divisor(200))
        self.assertEqual(1, get_biggest_divisor(202))
        self.assertEqual(1000, get_biggest_divisor(1000))
        self.assertEqual(10, get_biggest_divisor(1010))

    def test_get_best_interval_in_list(self):
        self.assertEqual(5, get_best_interval_in_list([3, 4, 5]))
        self.assertEqual(10, get_best_interval_in_list([9, 10, 11]))
        self.assertEqual(100, get_best_interval_in_list(list(range(1, 199))))
