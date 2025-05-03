from typing import Tuple, List
from path_datatype import Vector


class PathProcessor:
    def __init__(self, path_coords: list[Tuple[int, int]]):
        """
        Transforms specified list coordinates to a sequence of pixel vectors overlapping all specified coordinates.

        :param path_coords: specified list of 2-dimensional coordinates
        """
        self._path_coords = path_coords

    def create_path(self) -> list[Vector]:
        """
        Creates a list of translation vectors from specified coordinates. These translation vectors will overlap the
        specified coordinates at minimum. When difference between specified coordinates is oblique, a Manhattan interpolation
        method is used which generates at least 2 translation vectors.

        :return: a list of translation vectors guaranteed to overlap specified coordinates
        """
        travel_vectors = []
        last_coord = (0, 0)
        for path_coord in self._path_coords:
            x, y = path_coord
            last_x, last_y = last_coord
            dx = x - last_x
            dy = y - last_y
            if dx != 0:
                travel_vectors.append((dx, 0))
            if dy != 0:
                travel_vectors.append((0, dy))
        return travel_vectors
