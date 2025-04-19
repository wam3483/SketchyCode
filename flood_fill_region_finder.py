from PIL import Image
from typing import List
from collections import deque
from path_datatype import Point, Region

class FloodFillRegionFinder:

    def __init__(self, bitmap_img : Image.Image, min_region_size = 10):
        self._img = bitmap_img
        self._min_region_size = min_region_size

    def _is_pixel_black(self, pixel_coord: Point, black_threshold : float = .5) -> bool:
        """
        Returns true if pixel at specified coordinate is black. Default implementation assumes luminosity less than
        specified threshold is considered black.

        :param pixel_coord: specified x-y coordinate

        :return: whether pixel at specified coordinate is black
        """
        pixel = self._img.getpixel(pixel_coord)
        if isinstance(pixel, int):
            return pixel == 0
        else:
            x,y,z = pixel
            luminosity = (x + y + z) / 255
            return luminosity < black_threshold

    def find_regions(self) -> List[Region]:
        """
        Identifies sets of contiguous black pixels from specified image.

        :return: contiguous sets of black pixels from specified image
        """
        regions = [Region]
        visited_coords = set[Point]()
        for y in range(0, self._img.height):
            for x in range(0, self._img.width):
                pixel_coordinate = (x,y)
                if not pixel_coordinate in visited_coords and self._is_pixel_black(pixel_coordinate):
                        region = self._select_pixels_from(pixel_coordinate, visited_coords)
                        if len(region) > self._min_region_size:
                            regions.append(region)
        return regions

    def _select_pixels_from(self, pixel_coord : Point, previously_considered_coordinates : set[Point]) -> Region:
        """
        Performs a depth-first selection of all black pixels beginning at specified pixel coordinate. As this
        implementation requires a set of coordinates to track which coordinates have been considered, this function
        is internal.

        Time complexity: O(n)
        Space complexity: O(n)

        :param pixel_coord: specified pixel coordinate
        :param previously_considered_coordinates: specified pixel coordinates that are a part of a contiguous region

        :return: a contiguous region of pixels reachable from specified pixel coordinate.
        """
        stack = deque()
        stack.append(pixel_coord)
        selected_region = Region()
        while stack:
            next_pixel_coord = stack.pop()
            x,y = next_pixel_coord

            if (0 <= x < self._img.width and 0 <= y < self._img.height
                and not next_pixel_coord in previously_considered_coordinates
                and self._is_pixel_black(next_pixel_coord)):
                    previously_considered_coordinates.add(next_pixel_coord)
                    selected_region.append(next_pixel_coord)
                    stack.extend([
                        (x, y+1),
                        (x-1, y),
                        (x+1, y),
                        (x, y-1)
                    ])
        return selected_region