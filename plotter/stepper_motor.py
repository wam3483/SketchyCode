import string
import time

from plotter.gpio_pin import GPIO_Pin


class StepperMotor:

    def __init__(self,
                 direction_pin : GPIO_Pin, step_pin : GPIO_Pin, enable_pin : GPIO_Pin,
                 steps_per_rotation : int,
                 name : string):
        self._dir_pin = direction_pin
        self._step_pin = step_pin
        self._enable_pin = enable_pin
        self._steps_per_rotation = steps_per_rotation
        self._degrees_per_sec = 1.0
        self._name = name

    def set_speed(self, degrees_per_sec : float):
        self._degrees_per_sec = degrees_per_sec

    def validate(self) -> bool:
        is_config_correct = self._dir_pin.validate() and self._step_pin.validate() and self._enable_pin.validate()
        return is_config_correct

    def rotate(self, degrees : float):
        num_steps = self._get_number_steps(degrees)

        step_delay_secs = self._get_step_delay_secs()

        delay_per_half_step = step_delay_secs / 2
        for x_step_count in range(int(num_steps)):
            if not self._step_pin.write(True):
                break
            time.sleep(delay_per_half_step)
            if not self._step_pin.write(False):
                break
            time.sleep(delay_per_half_step)

    def _get_step_delay_secs(self):
        rotations_per_sec = self._degrees_per_sec / 360.0
        steps_per_sec = self._steps_per_rotation * rotations_per_sec
        step_delay_secs = 1 / steps_per_sec
        return step_delay_secs

    def _get_number_steps(self, degrees : float):
        num_rotations = degrees / 360.0
        num_steps = self._steps_per_rotation * num_rotations
        return num_steps