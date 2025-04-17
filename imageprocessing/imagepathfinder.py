from PIL import Image
from typing import Tuple, List
from collections import deque

Point = Tuple[int, int]
Region = List[Point]

class ImagePathFinder:

    def __init__(self, bitmap_img : Image.Image, min_region_size = 10):
        self._img = bitmap_img
        self._min_region_size = min_region_size

    def find_regions(self) -> List[Region]:
        regions = []
        visited_points = set()
        for y in range(0, self._img.height):
            for x in range(0, self._img.width):
                if not (x,y) in visited_points and self._is_pixel_black((x,y)):
                        region = self._select_pixels_from((x,y), visited_points)
                        if len(region) > self._min_region_size:
                            regions.append(region)
        return regions

    def _is_pixel_black(self, point: Point) -> bool:
        pixel = self._img.getpixel(point)
        return pixel == (0, 0, 0) or (isinstance(pixel, int) and pixel == 0)

    def _select_pixels_from(self, point : Point, visited_points : set[Point]) -> Region:
        stack = deque()
        stack.append(point)
        selected_region = Region()
        while stack:
            next_point = stack.pop()
            x,y = next_point

            if (0 <= x < self._img.width and 0 <= y < self._img.height
                and not next_point in visited_points
                and self._is_pixel_black(next_point)):
                    visited_points.add(next_point)
                    selected_region.append(next_point)
                    stack.extend([
                        (x, y+1),
                        (x-1, y),
                        (x+1, y),
                        (x, y-1)
                    ])
        return selected_region