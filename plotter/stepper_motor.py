import logging
import warnings

import pigpio
import string
import time

from plotter.gpio_pin import GPIO_Pin
from plotter.gpio_pin_base import GPIOPinBase


class StepperMotor:

    def __init__(self,
                 pi : pigpio.pi,
                 direction_pin : GPIOPinBase, step_pin : GPIOPinBase, enable_pin : GPIOPinBase,
                 steps_per_rotation : int,
                 backlash_correction_steps : int,
                 name : string):
        self._dir_pin = direction_pin
        self._step_pin = step_pin
        self._enable_pin = enable_pin
        self._steps_per_rotation = steps_per_rotation
        self._backlash_correction_steps = backlash_correction_steps
        self._velocityFunc_degrees_per_sec = lambda alpha: 360
        self._name = name
        self._pi = pi
        self._lastDirectionState = False

    def backlash_correction_degrees(self) -> float:
        return self._backlash_correction_steps / self._steps_per_rotation

    @classmethod
    def from_pins(cls, pi : pigpio.pi, direction_pin : int, step_pin : int, enable_pin : int,
                  steps_per_rotation : int,
                  backlash_correction_steps : int,
                  name : string):
        direction_gpio = GPIO_Pin(direction_pin, pi, pigpio.OUTPUT)
        step_gpio = GPIO_Pin(step_pin, pi, pigpio.OUTPUT)
        enable_gpio = GPIO_Pin(enable_pin, pi, pigpio.OUTPUT)
        enable = enable_gpio.validate()
        step = step_gpio.validate()
        direction = direction_gpio.validate()
        if not (enable and step and direction):
            warnings.warn(f"Motor [{name}] failed to config."
                          f" enablePin=[{enable_pin}], enable_success=[{enable}],"
                          f" dirPin=[{direction_pin}], dir_success=[{direction}],"
                          f" stepPin=[{step_pin}], step_success=[{step}]")
        else:
            logging.info(f"Motor [{name}] configured successfully.")

        return StepperMotor(pi, direction_gpio, step_gpio, enable_gpio,
                            steps_per_rotation, backlash_correction_steps, name)

    def set_speed(self, degrees_per_sec):
        self._velocityFunc_degrees_per_sec = degrees_per_sec

    def validate(self) -> bool:
        is_config_correct = self._dir_pin.validate() and self._step_pin.validate() and self._enable_pin.validate()
        return is_config_correct

    def rotate(self, degrees: float):
        logging.info(f"Motor [{self._name}]: set enablePin[{self._enable_pin.get_pin()}] HIGH")
        if not self._enable_pin.write(True):
            warnings.warn(f"Motor [{self._name}]: failed to set enable pin HIGH")

        current_dir_state = degrees > 0

        logging.info(f"Motor [{self._name}]: set dirPin[{self._dir_pin.get_pin()}] {current_dir_state}")
        if not self._dir_pin.write(current_dir_state):
            warnings.warn(f"Motor [{self._name}]: failed to set direction pin [{self._dir_pin.get_pin()}] to [{current_dir_state}]")

        backlash_correction_steps = 0
        if self._lastDirectionState != current_dir_state:
            backlash_correction_steps = self._backlash_correction_steps
        num_steps = int(self._steps_per_rotation * abs(degrees / 360) + backlash_correction_steps)
        self._lastDirectionState = current_dir_state

        start_velocity = self._velocityFunc_degrees_per_sec(0)
        logging.info(f"Motor [{self._name}] rotate: degrees={degrees}, steps={num_steps}, startVel={start_velocity:.2f} deg/s")

        self._send_wave(num_steps)

        logging.info(f"Motor [{self._name}]: set enablePin[{self._enable_pin.get_pin()}] LOW")
        if not self._enable_pin.write(False):
             warnings.warn(f"Motor [{self._name}]: failed to set enable pin LOW")

    def _send_wave(self, num_steps : int):
        MAX_STEPS_PER_WAVE = 2000
        for chunk_start in range(0, num_steps, MAX_STEPS_PER_WAVE):
            chunk_steps = min(MAX_STEPS_PER_WAVE, num_steps - chunk_start)
            pulses = []

            for i in range(chunk_steps):
                normalized_step_count = (chunk_start + i) / num_steps
                degrees_per_sec = self._velocityFunc_degrees_per_sec(normalized_step_count)
                steps_per_sec = self._get_steps_per_second(degrees_per_sec)
                delay_us = int(1_000_000 / steps_per_sec / 2)

                step_pin_mask = 1 << self._step_pin.get_pin()
                pulses.append(pigpio.pulse(step_pin_mask, 0, delay_us))
                pulses.append(pigpio.pulse(0, step_pin_mask, delay_us))

            try:
                self._pi.wave_clear()
                self._pi.wave_add_generic(pulses)
                wave_id = self._pi.wave_create()
                if wave_id < 0:
                    warnings.warn(f"Motor [{self._name}]: wave_create failed with code {wave_id}")
                    break

                self._pi.wave_send_once(wave_id)
                while self._pi.wave_tx_busy():
                    time.sleep(0.001)

                self._pi.wave_delete(wave_id)

            except Exception as e:
                warnings.warn(f"Motor [{self._name}]: Exception during wave send: {e}")
                break

    def _get_steps_per_second(self, degrees_per_sec : float) -> int:
        num_rotations = degrees_per_sec / 360.0
        num_steps = self._steps_per_rotation * num_rotations
        return int(num_steps)