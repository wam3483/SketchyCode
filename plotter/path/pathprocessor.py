import logging
from typing import Tuple, List

from numpy import sign

from plotter.path.path_datatype import Vector



def create_path(path_coords: list[Tuple[int, int]]) -> list[Vector]:
    """
    Creates a list of translation vectors from specified coordinates. These translation vectors will overlap the
    specified coordinates at minimum. When difference between specified coordinates is oblique, a Manhattan interpolation
    method is used which generates at least 2 translation vectors.

    :return: a list of translation vectors guaranteed to overlap specified coordinates
    """
    travel_vectors = []
    x_cursor_position = 0
    y_cursor_position = 0
    x_new = 0
    y_new = 0
    x_moving = False
    y_moving = False

    for i, path_coord in enumerate(path_coords):

        x_new, y_new = path_coord

        dx = x_new - x_cursor_position
        dy = y_new - y_cursor_position

        # y changed and x changed
        if y_new != y_cursor_position and x_new != x_cursor_position:
            if x_moving:
                travel_vectors.append((dx, 0))
                travel_vectors.append((0, dy))
            elif y_moving:
                travel_vectors.append((0, dy))
                travel_vectors.append((dx, 0))
            else:
                travel_vectors.append((dx, 0))
                travel_vectors.append((0, dy))
            x_cursor_position = x_new
            y_cursor_position = y_new
            x_moving = False
            y_moving = False
        # x has changed some # of times but y has not.
        elif x_new != x_cursor_position:
            x_moving = True
        # y has changed some # of times but x has not.
        elif y_new != y_cursor_position:
            y_moving = True

    return travel_vectors


# class PathProcessor:
    # def __init__(self, path_coords: list[Tuple[int, int]]):
    #     """
    #     Transforms specified list coordinates to a sequence of pixel vectors overlapping all specified coordinates.
    #
    #     :param path_coords: specified list of 2-dimensional coordinates
    #     """
    #     self._path_coords = path_coords

