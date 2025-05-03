from typing import Optional

from plotter.gpio_pin_base import GPIOPinBase


class GPIOPinNull(GPIOPinBase):

    def get_pin(self)->int:
        return 0

    def configure(self) -> bool:
        return True

    def validate(self):
        raise NotImplementedError

    def get_config(self) -> Optional[bool]:
        return True

    def write(self, pin_state: bool) -> bool:
        return True