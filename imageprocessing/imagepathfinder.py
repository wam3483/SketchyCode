import threading
from PIL import Image
import time
from typing import Tuple, Optional
from collections import deque

class ImagePathFinder:
    def find_path(self, bitmapImage : Image.ImageFile) -> Tuple[int, int]:
        """
            Scans the image and returns the coordinates of the starting point of a path.
            Returns:
                Tuple[int, int]: Coordinates of the start of the path, or (-1, -1) if not found.
        """
        visited_points = set()
        for y in range(0, bitmapImage.height):
            for x in range(0, bitmapImage.width):
                if not (x,y) in visited_points:
                    visited_points.add((x,y))
                    self._find_region((x,y), visited_points, bitmapImage)

        return (-1, -1)

    def _find_closest_pixel_to_origin(self, image: Image.ImageFile) -> Optional[Tuple[int,int]]:
        min_distance = image.width * image.height
        start_x = -1
        start_y = -1
        for y in range(0, image.height):
            if y*y > min_distance:
                break
            for x in range(0, image.width):
                pixel = image.getpixel(x, y)
                if pixel == (0, 0, 0) or (isinstance(pixel, int) and pixel == 0):
                    distance = x*x + y*y
                    if distance < min_distance:
                        min_distance = distance
                        start_x = x
                        start_y = y

        if start_x == -1 and start_y == -1:
            return None

        return (start_x, start_y)


    def _find_region(self,  start_point : Tuple[int,int], visited_points : set, image: Image.ImageFile) -> Optional[Tuple[int,int]]:
        x_start, y_start = start_point

        for y in range(y_start, image.height):
            for x in range(x_start, image.width):
                if not (x,y) in visited_points:
                    visited_points.add((x,y))
                    pixel = image.getpixel(x, y)
                    if pixel == (0, 0, 0) or (isinstance(pixel, int) and pixel == 0):
                        return (x, y)

        return None

