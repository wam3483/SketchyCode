from dataclasses import dataclass

@dataclass
class ConfigSettings:
    xBacklashPixels: float
    yBacklashPixels: float
    xDegreesPerPixel: float
    yDegreesPerPixel: float
    drawSpeed_PixelsPerSec: float
    overdraw_pixels : float