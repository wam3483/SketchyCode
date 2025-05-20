import logging
from collections import deque
from typing import Tuple, List, Set

from numpy import sign

from data.Vector import Vector
from plotter.path.path_datatype import Region


def _find_path_between(start: Vector, end: Vector, pixels: Set[Vector], directions: List[Vector]) -> List[Vector]:
    """
    Finds the shortest Manhattan path from `start` to `end` using BFS, restricted to the provided set of contiguous coordinates/pixels.
    """
    queue = deque([(start, [])])
    visited = set()

    while queue:
        pos, backtrack_path = queue.popleft()
        if pos == end:
            return backtrack_path
        visited.add(pos)
        x, y = pos.x, pos.y
        for dir_vector in directions:
            neighbor = Vector(x + dir_vector.x, y + dir_vector.y)
            if neighbor in pixels and neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, backtrack_path + [neighbor]))

    return []


def trace_with_backtracking(pixels: Set[Vector], start: Vector) -> List[Vector]:
    visited = set()
    path = []
    stack = [start]
    directions = [Vector(0, -1), Vector(1, 0), Vector(0, 1), Vector(-1, 0)]  # Up, Right, Down, Left
    current = start
    while stack:
        next_pos = stack.pop()
        if next_pos in visited:
            continue

        #plot path to next position by backtracking
        distance_to_next_pos = abs(current.x - next_pos.x) + abs(current.y - next_pos.y)
        is_next_move_adjacent = 0 <= distance_to_next_pos <= 1
        if not is_next_move_adjacent:
            backtrack_path = _find_path_between(current, next_pos, pixels, directions)
            path.extend(backtrack_path)
            visited.update(backtrack_path)
            current = next_pos
        else:
            path.extend([next_pos])
            visited.add(next_pos)
            current = next_pos

        x, y = current.x, current.y
        for dir_vector in directions:
            neighbor = Vector(x + dir_vector.x, y + dir_vector.y)
            if neighbor in pixels and neighbor not in visited:
                stack.append(neighbor)

    return path

def vectorize_path_processor_func(points: List[Vector]) -> List[Vector]:
    """
    Creates a list of translation vectors from specified coordinates. These translation vectors will overlap the
    specified coordinates at minimum. When difference between specified coordinates is oblique, a Manhattan interpolation
    method is used which generates at least 2 translation vectors.

    Time complexity : O(n)
    Space complexity: O(n)

    :return: a list of translation vectors guaranteed to overlap specified coordinates
    """
    if len(points) < 2:
        return []

    vectors = []
    prev = points[0]
    dx = dy = 0

    for current in points[1:]:
        step_dx = current.x - prev.x
        step_dy = current.y - prev.y

        # Detect direction
        next_step_direction = (sign(step_dx), sign(step_dy))
        current_step_direction = (sign(dx), sign(dy))

        # If direction changes, commit previous vector
        if next_step_direction != current_step_direction and (dx != 0 or dy != 0):
            vectors.append(Vector(dx, dy))
            dx = dy = 0

        dx += step_dx
        dy += step_dy
        prev = current

    # Commit final vector
    if dx != 0 or dy != 0:
        vectors.append(Vector(dx, dy))

    return vectors

def get_translation_vectors(vectors : List[Vector]):
    all_translation_vectors = []
    #todo track cursor pos through iteration.
    #todo sort regions so that their begin and end points minimize distance (Traveling salesman?)
    cursor_pos = (0,0)
    for i, region in enumerate(vectors):
        region_set = set(region.region)
        region_path = trace_with_backtracking(region_set, region.region[0])

        vectors = vectorize_path_processor_func(region_path)

        if i > 0:
            # draw straight line paths to start of first region.
            # cursor pos is sum of all translation vectors
            cursor_pos = tuple(map(sum, zip(*all_translation_vectors)))
            start_point = region_path[0]
            dx = start_point[0]- cursor_pos[0]
            dy = start_point[1] - cursor_pos[1]
            all_translation_vectors.append((dx, dy))
        else:
            #
            cursor_pos = region_path[0]
            all_translation_vectors.append(cursor_pos)

        all_translation_vectors.extend(vectors)

    return all_translation_vectors

# class PathProcessor:
    # def __init__(self, path_coords: list[Tuple[int, int]]):
    #     """
    #     Transforms specified list coordinates to a sequence of pixel vectors overlapping all specified coordinates.
    #
    #     :param path_coords: specified list of 2-dimensional coordinates
    #     """
    #     self._path_coords = path_coords

