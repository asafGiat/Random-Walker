import unittest
from walker import *

class TestWalker(unittest.TestCase):
    def test_simple_walk(self):
        walker = Walker(SIMPLE_WALK)
        start_pos = walker.get_position()
        walker.walk()
        end_pos = walker.get_position()
        self.assertNotEqual(start_pos, end_pos, "Simple walk should change position")

    def test_square_walk(self):
        walker = Walker(SQUARE_WALK)
        start_pos = walker.get_position()
        walker.walk()
        end_pos = walker.get_position()
        self.assertNotEqual(start_pos, end_pos, "Square walk should change position")
        # Further tests can check if the movement is constrained to square grid logic

    def test_random_size_walk(self):
        walker = Walker(RANDOM_SIZE_WALK)
        start_pos = walker.get_position()
        walker.walk()
        end_pos = walker.get_position()
        self.assertNotEqual(start_pos, end_pos, "Random size walk should change position")

    def test_preferred_walk(self):
        walker = Walker(PREFERRED_WALK)
        start_pos = walker.get_position()
        walker.walk()
        end_pos = walker.get_position()
        self.assertNotEqual(start_pos, end_pos, "Preferred walk should change position")

if __name__ == '__main__':
    unittest.main()
