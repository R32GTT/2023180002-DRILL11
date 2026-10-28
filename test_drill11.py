import unittest
from unittest.mock import Mock, patch

import Drill11


class BoyStateMachineTests(unittest.TestCase):
    def setUp(self):
        self.image = Mock()
        self.load_image_patcher = patch('Drill11.load_image', return_value=self.image)
        self.load_image_patcher.start()
        self.addCleanup(self.load_image_patcher.stop)
        self.boy = Drill11.Boy()

    def test_starts_in_idle(self):
        self.assertEqual(self.boy.state, 'IDLE')


if __name__ == '__main__':
    unittest.main()
