import pigpio
import time
from path_datatype import VectorPath, Vector
import numpy as math

class XYPlotter:
    def __init__(self, steps_per_revolution : int,
                 revolutions_per_pixel: float,
                 microsec_per_step : float,
                 x_direction_pin : int, x_step_pin : int,
                 y_direction_pin : int, y_step_pin : int):

        self._steps_per_revolution = steps_per_revolution
        self._revolutions_per_pixel = revolutions_per_pixel
        self._microsec_per_step = microsec_per_step
        self._pi = pigpio.pi()

        self._x_direction_pin = x_direction_pin
        self._y_direction_pin = y_direction_pin
        self._x_step_pin = x_step_pin
        self._y_step_pin = y_step_pin

        self._pi.set_mode(x_direction_pin, pigpio.OUTPUT)
        self._pi.set_mode(x_step_pin, pigpio.OUTPUT)

        self._pi.set_mode(y_direction_pin, pigpio.OUTPUT)
        self._pi.set_mode(y_step_pin, pigpio.OUTPUT)

    def move(self, vector : Vector):
        x,y = vector
        move_x = x != 0
        move_y = y != 0
        # set direction for axis'
        if move_x:
            self._pi.write(self._x_direction_pin, math.sign(x))
        if move_y:
            self._pi.write(self._y_direction_pin, math.sign(y))
        time_per_half_step = self._microsec_per_step / 2
        if move_x:
            x_num_steps = x * self._revolutions_per_pixel * self._steps_per_revolution
            for x_step_count in range(int(x_num_steps)):
                self._pi.write(self._x_step_pin, 1)
                time.sleep(time_per_half_step)
                self._pi.write(self._x_step_pin, 0)
                time.sleep(time_per_half_step)
        if move_y:
            y_num_steps = y * self._revolutions_per_pixel * self._steps_per_revolution
            for y_step_count in range(int(y_num_steps)):
                self._pi.write(self._y_step_pin, 1)
                time.sleep(time_per_half_step)
                self._pi.write(self._y_step_pin, 0)
                time.sleep(time_per_half_step)

    def stop(self):
        self._pi.stop()