import logging
from typing import Optional

import pigpio

from plotter.gpio_pin_base import GPIOPinBase


class GPIO_Pin(GPIOPinBase):
    def __init__(self, pin_number : int, pi : pigpio.pi, pin_type : int):
        self._pin_number = pin_number
        self._pi = pi
        self._pin_type = pin_type
        self.configure()

    def get_pin(self) -> int:
        return self._pin_number

    def configure(self) -> bool:
        return self._pi.set_mode(self._pin_number, self._pin_type) == 0

    def validate(self):
        current_pin_type = self._pi.get_mode(self._pin_number)
        return current_pin_type == self._pin_type

    def get_config(self) -> Optional[bool]:
        '''
        Fetches pigpio pin configuration.
        :return: True if pin configured as output, false if input, and none otherwise
        '''
        current_pin_type = self._pi.get_mode(self._pin_number)
        match current_pin_type:
            case pigpio.OUTPUT:
                return True
            case pigpio.INPUT:
                return False
        return None

    def write(self, pin_state : bool) -> bool:
        pin_int = pigpio.HIGH if pin_state else pigpio.LOW
        result = self._pi.write(self._pin_number, pin_int)
        return result == 0