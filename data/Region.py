from typing import List, Tuple

import numpy

from data.Vector import Vector


class Region:
    def __init__(self, region: set[Vector]):
        self.region = region
        self.outline = self._get_outline()

    def _get_outline(self) -> List[Vector]:
        """
        Selects any pixels in given set which have no adjacent pixels.
        :param region: given set
        :return: all points in given set with at least one neighboring point not in given set
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        outline = []
        for point in self.region:
            for dx, dy in directions:
                neighbor = Vector(point.x + dx, point.y + dy)
                if neighbor not in self.region:
                    outline.append(point)
                    break
        return outline

    @staticmethod
    def distance(r1: 'Region', r2: 'Region') -> float:
        min_value = numpy.inf
        for p1 in r1.outline:
            for p2 in r2.outline:
                value = p1.dist(p2)
                if value < min_value:
                    min_value = value
        return min_value

    def get_nearest_connecting_points(self, other: 'Region') -> Tuple[Vector, Vector]:
        min_value = numpy.inf
        start = (0, 0)
        end = (0, 0)
        for p1 in self.outline:
            for p2 in other.outline:
                dist = p1.dist(p2)
                if dist < min_value:
                    min_value = dist
                    start = p1
                    end = p2
        return start, end