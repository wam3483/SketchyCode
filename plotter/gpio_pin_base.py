from typing import Optional


class GPIOPinBase:
    def get_pin(self) -> int:
        raise NotImplementedError
    def configure(self) -> bool:
        raise NotImplementedError
    def validate(self):
        raise NotImplementedError
    def get_config(self) -> Optional[bool]:
        raise NotImplementedError
    def write(self, pin_state: bool) -> bool:
        raise NotImplementedError