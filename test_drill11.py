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

    def test_run_moves_and_returns_to_idle_after_release(self):
        start_x = self.boy.x
        self.boy.handle_key_down(Drill11.SDLK_LEFT)
        self.boy.update(0.1)

        self.assertAlmostEqual(self.boy.x, start_x - 30)
        self.assertEqual(self.boy.state, 'RUN')

        self.boy.handle_key_up(Drill11.SDLK_LEFT)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.move_direction, 0)

    def test_autorun_speed_exceeds_normal_run_speed(self):
        normal_start_x = self.boy.x
        self.boy.handle_key_down(Drill11.SDLK_RIGHT)
        self.boy.update(0.1)
        normal_distance = self.boy.x - normal_start_x

        auto_boy = Drill11.Boy()
        auto_start_x = auto_boy.x
        auto_boy.handle_key_down(Drill11.SDLK_a)
        auto_boy.update(0.1)
        auto_distance = auto_boy.x - auto_start_x

        self.assertGreater(auto_distance, normal_distance)

    def test_autorun_returns_to_idle_after_five_seconds(self):
        self.boy.handle_key_down(Drill11.SDLK_a)
        auto_state = self.boy.machine.states['AUTORUN']
        auto_state.elapsed = Drill11.AUTORUN_DURATION - 0.01

        self.boy.update(0.02)

        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.move_direction, 0)


if __name__ == '__main__':
    unittest.main()
