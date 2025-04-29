import pigpio
import time
from path_datatype import VectorPath, Vector
import platform
import warnings
import logging

class XYPlotter:

    def __init__(self, pi, steps_per_revolution : int,
                 cycles_per_pixel: float,
                 motor_cycles_per_sec : float,
                 x_direction_pin : int, x_step_pin : int, x_enable_pin : int,
                 y_direction_pin : int, y_step_pin : int, y_enable_pin : int):

        self._pi = pi

        self.plotter_dimensions = (640, 480)

        self._motor_steps_per_cycle = steps_per_revolution
        self._motor_cycles_per_sec = motor_cycles_per_sec
        self._cycles_per_pixel = cycles_per_pixel

        self._x_direction_pin = x_direction_pin
        self._y_direction_pin = y_direction_pin
        self._x_step_pin = x_step_pin
        self._y_step_pin = y_step_pin

        self._x_enable_pin = x_enable_pin
        self._y_enable_pin = y_enable_pin

        self._on_raspberry = platform.system() == 'Linux'
        self._y_enabled = self._y_step_pin > 0 and self._y_direction_pin > 0 and self._y_enable_pin > 0 and self._on_raspberry
        self._x_enabled = self._x_step_pin > 0 and self._x_direction_pin > 0 and self._x_enable_pin > 0 and self._on_raspberry

        if self._x_enabled:
            dir_mode_success = self._set_pin_mode(self._x_direction_pin, pigpio.OUTPUT)
            step_mode_success = self._set_pin_mode(self._x_step_pin, pigpio.OUTPUT)
            enable_mode_success = self._set_pin_mode(self._x_enable_pin, pigpio.OUTPUT)

            if not dir_mode_success or not step_mode_success or not enable_mode_success:
                warnings.warn(f"plotter x axis disabled, failed to config pins. "
                              f"enable_pin[{self._x_enable_pin}]={enable_mode_success}"
                              f"dir_pin[{self._x_direction_pin}]={dir_mode_success}, "
                              f"step_pin[{self._x_step_pin}]={step_mode_success}")
        else:
            warnings.warn(f"plotter x axis disabled. onLinux=[{self._on_raspberry}],"
                          f" stepPin=[{self._x_step_pin}],"
                          f" dirPin=[{self._x_direction_pin}],"
                          f" enablePin=[{self._x_enable_pin}]")

        if self._y_enabled:
            dir_mode_success = self._set_pin_mode(self._y_direction_pin, pigpio.OUTPUT)
            step_mode_success = self._set_pin_mode(self._y_step_pin, pigpio.OUTPUT)
            enable_mode_success = self._set_pin_mode(self._y_enable_pin, pigpio.OUTPUT)

            if not dir_mode_success or not step_mode_success or not enable_mode_success:
                warnings.warn(f"Plotter Y axis disabled, failed to config pins. "
                              f"enable_pin[{self._y_enable_pin}] ready={enable_mode_success}"
                              f"dir_pin[{self._y_direction_pin}] ready={dir_mode_success}, "
                              f"step_pin[{self._y_step_pin}] ready={step_mode_success}")
            else:
                logging.info("y axis configured")
        else:
            warnings.warn(f"Plotter Y axis disabled. Invalid configuration. onLinux=[{self._on_raspberry}],"
                          f" stepPin=[{self._y_step_pin}],"
                          f" dirPin=[{self._y_direction_pin}],"
                          f" enablePin=[{self._y_enable_pin}]")

    def move(self, vector : Vector):
        # set direction for axis'
        if self._on_raspberry:
            x,y = vector
            move_x = x != 0 and self._x_enabled
            move_y = y != 0 and self._y_enabled

            # enable motor, set direction.
            if move_x:
                x_dir = pigpio.HIGH if x > 0 else pigpio.LOW
                self._set_pin(self._x_enable_pin, pigpio.HIGH)
                self._set_pin(self._x_direction_pin, x_dir)
                logging.info(f"GPIO set direction x pin[{self._x_direction_pin}] = {x_dir}")
            if move_y:
                y_dir = pigpio.HIGH if y > 0 else pigpio.LOW
                self._set_pin(self._y_enable_pin, pigpio.HIGH)
                self._set_pin(self._y_direction_pin, y_dir)
                logging.info(f"GPIO set direction y pin[{self._y_direction_pin}] = {y_dir}")

            #calculate delay time between each gpio step pin state change
            steps_per_sec = self._motor_cycles_per_sec * self._motor_steps_per_cycle
            step_delay_hz = 1 / steps_per_sec
            logging.info(f"step delay = {step_delay_hz}hz")

            if move_x:
                x_num_steps = abs(x) * self._cycles_per_pixel * self._motor_steps_per_cycle
                logging.info(f"movement will take {step_delay_hz * x_num_steps} sec")
                logging.info(f"x steps = {int(x_num_steps)} = abs({x}) * {self._cycles_per_pixel} * {self._motor_steps_per_cycle}")
                self._pulse_pin(int(x_num_steps), self._x_step_pin, step_delay_hz)
                self._set_pin(self._x_enable_pin, pigpio.LOW)

            if move_y:
                y_num_steps = abs(y) * self._cycles_per_pixel * self._motor_steps_per_cycle
                logging.info(f"y steps = {int(y_num_steps)} = abs({y}) * {self._cycles_per_pixel} * {self._motor_steps_per_cycle}")
                logging.info(f"movement will take {step_delay_hz * y_num_steps}")
                self._pulse_pin(int(y_num_steps), self._y_step_pin, step_delay_hz)
                self._set_pin(self._y_enable_pin, pigpio.LOW)

    def _pulse_pin(self, pulse_count: int, pin : int, delay_per_pulse : float):
        delay_per_half_step = delay_per_pulse / 2
        for x_step_count in range(int(pulse_count)):
            if not self._set_pin(pin, pigpio.HIGH):
                break
            time.sleep(delay_per_half_step)

            if not self._set_pin(pin, pigpio.LOW):
                break
            time.sleep(delay_per_half_step)

    def _set_pin(self, pin : int, state : int) -> bool:
        result = self._pi.write(pin, state)
        if result != 0:
            warnings.warn(f'failed setting pin[{pin}] = {state}. error code = {result}')
        return result == 0

    def _set_pin_mode(self,pin : int, mode : int) -> bool:
        result = self._pi.set_mode(pin, mode)
        if result != 0:
            warnings.warn(f'failed setting MODE for pin[{pin}] = {mode}. error code = {result}')
        return result == 0

    def move_to_origin(self):
        w,h = self.plotter_dimensions
        self.move(Vector(-w, 0))
        self.move(Vector(-h, 0))

    def stop(self):
        if self._on_raspberry:
            self._pi.stop()