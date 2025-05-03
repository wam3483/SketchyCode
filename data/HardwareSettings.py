from dataclasses import dataclass

@dataclass
class HardwareSettings:
    xStepPin: int
    xEnablePin: int
    xDirectionPin: int
    yStepPin: int
    yEnablePin: int
    yDirectionPin: int
    stepsPerCycle: int