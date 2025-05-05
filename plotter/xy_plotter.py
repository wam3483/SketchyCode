import logging

import pigpio

from dao.SettingsFileDao import SettingsFileDao
from data.Utils import on_raspberry
from plotter.gpio_pin_null import GPIOPinNull
from plotter.path.path_datatype import Vector

from plotter.stepper_motor import StepperMotor


def _pixels_to_degrees(pixels : float, cycles_per_pixel : float) -> float:
    return pixels * cycles_per_pixel * 360


class XYPlotter:

    def __init__(self,
                 pi: pigpio.pi,
                 x_cycles_per_pixel: float,
                 y_cycles_per_pixel: float,
                 x_motor : StepperMotor,
                 y_motor : StepperMotor):

        self.plotter_dimensions = (550, 400)

        self.x_motor = x_motor
        self.y_motor = y_motor
        self._pi = pi
        self._x_cycles_per_pixel = x_cycles_per_pixel
        self._y_cycles_per_pixel = y_cycles_per_pixel
        self.invert_x = True
        self.invert_y = False

    @classmethod
    def init_plotter(cls, pi: pigpio.pi, settings_repo : SettingsFileDao):
        hardware_settings = settings_repo.get_hardware_settings()
        config_settings = settings_repo.get_config_settings()

        motor_x = StepperMotor(pi, GPIOPinNull(), GPIOPinNull(), GPIOPinNull(),
                               hardware_settings.stepsPerCycle, 0,"x-motor")
        motor_y = StepperMotor(pi, GPIOPinNull(), GPIOPinNull(), GPIOPinNull(),
                               hardware_settings.stepsPerCycle, 0,"y-motor")
        if on_raspberry:
            x_backlash_correction_steps = int((config_settings.xBacklashPixels * config_settings.xDegreesPerPixel) / 360 * hardware_settings.stepsPerCycle)
            y_backlash_correction_steps = int((config_settings.yBacklashPixels * config_settings.yDegreesPerPixel) / 360 * hardware_settings.stepsPerCycle)
            motor_x = StepperMotor.from_pins(pi,
                                             hardware_settings.xDirectionPin,
                                             hardware_settings.xStepPin,
                                             hardware_settings.xEnablePin,
                                             hardware_settings.stepsPerCycle,
                                             x_backlash_correction_steps,
                                             "x-motor")  # 17, 27, 22, 3200, "x_motor")
            logging.info(f"x-motor initialized:"
                         f"\n\tstepPin=[{hardware_settings.xStepPin}]"
                         f"\n\tdirPin=[{hardware_settings.xDirectionPin}]"
                         f"\n\tenablePin=[{hardware_settings.xEnablePin}]"
                         f"\n\tstepsPerCycle=[{hardware_settings.stepsPerCycle}]"
                         f"\n\tx-backlash-correction-steps=[{x_backlash_correction_steps}]")
            motor_y = StepperMotor.from_pins(pi,
                                             hardware_settings.yDirectionPin,
                                             hardware_settings.yStepPin,
                                             hardware_settings.yEnablePin,
                                             hardware_settings.stepsPerCycle,
                                             y_backlash_correction_steps,
                                             "y-motor")  # 23, 24, 25, 3200, "y_motor")
            logging.info(f"y-motor initialized:"
                         f"\n\tstepPin=[{hardware_settings.yStepPin}]"
                         f"\n\tdirPin=[{hardware_settings.yDirectionPin}]"
                         f"\n\tenablePin=[{hardware_settings.yEnablePin}]"
                         f"\n\tstepsPerCycle=[{hardware_settings.stepsPerCycle}]"
                         f"\n\ty-backlash-correction-steps=[{y_backlash_correction_steps}]")

        degrees_per_sec = config_settings.drawSpeed_PixelsPerSec * config_settings.xDegreesPerPixel
        motor_x.set_speed(lambda alpha: degrees_per_sec)
        motor_y.set_speed(lambda alpha: degrees_per_sec)

        result = XYPlotter(pi,
                           config_settings.xDegreesPerPixel / 360,
                           config_settings.yDegreesPerPixel / 360,
                           motor_x,
                           motor_y)
        return result

    def move(self, pixel_vector : Vector):
        x,y = pixel_vector
        move_x = x != 0
        move_y = y != 0

        if move_x:
            x_degrees = _pixels_to_degrees(x, self._x_cycles_per_pixel)

            invert_x_mult = -1 if self.invert_x else 1
            self.x_motor.rotate(x_degrees * invert_x_mult)

        if move_y:
            y_degrees = _pixels_to_degrees(y, self._y_cycles_per_pixel)

            invert_y_mult = -1 if self.invert_y else 1
            self.y_motor.rotate(y_degrees * invert_y_mult)

    def reset_cursor(self):
        width, height = self.plotter_dimensions
        self.move(Vector(-width, 0))
        self.move(Vector(-height, 0))
        x_pixel_backlash = self.x_motor.backlash_correction_degrees() / 360 * self._x_cycles_per_pixel
        y_pixel_backlash = self.y_motor.backlash_correction_degrees() / 360 * self._y_cycles_per_pixel

        self.move(Vector(-x_pixel_backlash, 0))
        self.move(Vector(0, -y_pixel_backlash))