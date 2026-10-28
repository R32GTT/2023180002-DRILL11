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

    def test_a_key_enters_autorun(self):
        self.boy.handle_key_down(Drill11.SDLK_a)

        self.assertEqual(self.boy.state, 'AUTORUN')

    def test_left_and_right_share_run_state(self):
        state_names = set(self.boy.machine.states)
        self.assertEqual(state_names, {'IDLE', 'RUN', 'AUTORUN'})

        self.boy.handle_key_down(Drill11.SDLK_LEFT)
        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.move_direction, -1)

        self.boy.handle_key_up(Drill11.SDLK_LEFT)
        self.boy.handle_key_down(Drill11.SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.move_direction, 1)


if __name__ == '__main__':
    unittest.main()
