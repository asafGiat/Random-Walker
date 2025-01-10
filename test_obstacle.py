import unittest
from obstacle import *

class TestObstacle(unittest.TestCase):
    def setUp(self):
        self.obstacle = Obstacle(1, 1, 0.5)

    def test_obstacle_position(self):
        self.assertEqual(self.obstacle.position, (1, 1), "Obstacle position should be initialized correctly")

    def test_obstacle_size(self):
        self.assertEqual(self.obstacle.get_size(), 0.5, "Obstacle size should be initialized correctly")

if __name__ == '__main__':
    unittest.main()
