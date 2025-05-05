import platform

from PIL.Image import Image

on_raspberry = platform.system() == 'Linux'

def get_image_metadata(img : Image):
    return {
        "Mode": f"{img.mode}",
        "Size": f"{img.size}",
        "Info": f"{img.info}",
    }