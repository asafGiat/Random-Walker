import unittest
from portal import *

class TestPortal(unittest.TestCase):
    def test_portal_transport(self):
        portal = Portal((0, 0), (10, 10))
        self.assertEqual(portal.transport((0, 0)), (10, 10), "Transport to opposite endpoint failed")
        self.assertEqual(portal.transport((10, 10)), (0, 0), "Transport to opposite endpoint failed")
        self.assertEqual(portal.transport((5, 5)), (5, 5), "Non-endpoint position should not transport")

if __name__ == '__main__':
    unittest.main()
