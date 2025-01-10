import unittest
from unittest.mock import Mock, patch
from board import Board, Walker, Obstacle, Portal

class TestBoard(unittest.TestCase):
    def setUp(self):
        # Mock the Walker, Obstacle, and Portal
        self.walker = Mock(spec=Walker)
        self.walker.get_position.return_value = (0, 0)
        self.obstacle = Obstacle(1, 1, 0.5)  # Using real obstacle for simplicity
        self.portal = Portal((5, 5), (10, 10))
        self.board = Board(self.walker)

    def test_add_obstacle(self):
        self.board.add_obstacle(self.obstacle)
        self.assertIn(self.obstacle, self.board._Board__obstacles, "Obstacle should be added to the board")

    def test_add_portal(self):
        self.board.add_portal(self.portal)
        self.assertIn(self.portal, self.board._Board__portales, "Portal should be added to the board")

    def test_do_move_no_obstacles(self):
        # Assume the walker can move without encountering obstacles
        self.walker.get_position.side_effect = [(0, 0), (1, 1)]  # Simulate walking
        self.board.do_move()
        self.walker.walk.assert_called_once()
        self.assertTrue(self.board.do_move(), "Movement should succeed without obstacles")

    def test_portal_interaction(self):
        # Test that the walker is transported correctly
        self.board.add_portal(self.portal)
        self.walker.get_position.side_effect = [(5, 5), (10, 10)]
        self.board.do_move()
        self.walker.portal_walk.assert_called()

    def test_obstacle_interaction(self):
        # Test that movement fails when encountering an obstacle
        self.board.add_obstacle(self.obstacle)
        self.walker.get_position.side_effect = [(0, 0), (1, 1), (1, 1)]  # Walker tries to move but can't
        self.assertFalse(self.board.do_move(), "Walker should not move successfully due to an obstacle")


if __name__ == '__main__':
    unittest.main()
