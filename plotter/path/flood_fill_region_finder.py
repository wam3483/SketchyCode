import math

from PIL import Image
from typing import List, Tuple
from collections import deque

from data.Vector import Vector
from plotter.path.path_datatype import Region


class FloodFillRegionFinder:

    def __init__(self, bitmap_img : Image.Image, min_region_size = 10, black_threshold : float = .5):
        self._img = bitmap_img
        self._min_region_size = min_region_size
        self.black_threshold = black_threshold

    def _is_pixel_black(self, pixel_coord: Vector) -> bool:
        """
        Returns true if pixel at specified coordinate is black. Default implementation assumes luminosity less than
        specified threshold is considered black.

        :param pixel_coord: specified x-y coordinate

        :return: whether pixel at specified coordinate is black
        """
        pixel = self._img.getpixel((pixel_coord.x,pixel_coord.y))
        if isinstance(pixel, int):
            return pixel != 0
        else:
            x,y,z = pixel
            luminosity = (x + y + z) / 3 / 255
            return luminosity < self.black_threshold

    def get_outline(self, region : set[Vector]) -> List[Vector]:
        """
        Selects any pixels in given set which have no adjacent pixels.
        :param region: given set
        :return: all points in given set with at least one neighboring point not in given set
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        outline : List[Vector] = []
        for point in region:
            for dx, dy in directions:
                neighbor = Vector(point.x + dx, point.y + dy)
                if neighbor not in region:
                    outline.append(neighbor)
        return outline

    def shortest_distance_between_points(self, set1 : List[Vector], set2 : List[Vector]) -> List[Vector]:
        min_distance = math.inf
        p1 = (0,0)
        p2 = (0,0)
        for x1, y1 in set1:
            for x2, y2 in set2:
                distance = abs(x1 - x2) + abs(y1 - y2)
                if distance < min_distance:
                    p1 = (x1,y1)
                    p2 = (x2,y2)
                    min_distance = distance
        return [p1, p2]

    def find_regions(self) -> List[Region]:
        """
        Identifies sets of contiguous black pixels from specified image.

        :return: contiguous sets of black pixels from specified image
        """
        regions : List[Region] = []
        visited_coords = set[Vector]()
        for y in range(0, self._img.height):
            for x in range(0, self._img.width):
                pixel_coordinate = Vector(x,y)
                if not pixel_coordinate in visited_coords and self._is_pixel_black(pixel_coordinate):
                        region = self._select_pixels_from(pixel_coordinate, visited_coords)
                        if len(region.region) >= self._min_region_size:
                            regions.append(region)
        return regions

    def _select_pixels_from(self, pixel_coord : Vector, previously_considered_coordinates : set[Vector]) -> Region:
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
        selected_region = set()
        while stack:
            next_pixel_coord = stack.pop()
            x,y = next_pixel_coord.x, next_pixel_coord.y

            if (0 <= x < self._img.width and 0 <= y < self._img.height
                and not next_pixel_coord in previously_considered_coordinates
                and self._is_pixel_black(next_pixel_coord)):
                    previously_considered_coordinates.add(next_pixel_coord)
                    selected_region.add(next_pixel_coord)
                    stack.extend([
                        Vector(x, y+1),
                        Vector(x-1, y),
                        Vector(x+1, y),
                        Vector(x, y-1)
                    ])
        return Region(selected_region)