from typing import List

import numpy
from PIL.Image import Image

from data.PlotterInstruction import PlotterInstruction
from data.PlotterInstructionConfig import PlotterInstructionConfig
from data.Region import Region
from data.Vector import Vector
from data.graph import Graph
from plotter.path.flood_fill_region_finder import FloodFillRegionFinder
from plotter.path.plotter_path_calc import vectorize_path_processor_func, trace_with_backtracking


class PlotterInstructionService:
    def __init__(self, config : PlotterInstructionConfig = PlotterInstructionConfig()):
        self.config = config

    def get_plotter_instructions(self, rgb_img : Image) -> PlotterInstruction:
        # select contiguous regions with flood fill
        flood_fill_finder = FloodFillRegionFinder(rgb_img,
                                                  self.config.min_region_size,
                                                  self.config.bitmap_luminosity_threshold)
        regions = flood_fill_finder.find_regions()
        all_region_outlines = []
        for r in regions:
            all_region_outlines.append(set(r.outline))

        # connect the closest contiguous sets of pixels using Traveling salesman
        fully_connected_region_graph = Graph.traveling_salesman_graph(regions, distance_func=Region.distance)

        # union all the contiguous pixel sets together
        union_of_regions = set[Vector]()
        for region in regions:
            for point in region.region:
                union_of_regions.add(point)

        # add pixels in between contiguous regions
        all_connecting_paths = []
        visited = set()
        for vertex in fully_connected_region_graph.graph:
            neighbors = fully_connected_region_graph.graph[vertex]
            visited.add(vertex)
            for neighbor in neighbors:
                if neighbor not in visited:
                    nearest_points = vertex.get_nearest_connecting_points(neighbor)
                    start, end = nearest_points
                    connecting_path = self.get_connecting_path(start, end)
                    all_connecting_paths.append(set(connecting_path))
                    union_of_regions.update(connecting_path)

        # get point nearest origin to start from path from
        starting_point = self.get_nearest_point(union_of_regions)
        start_connecting_path = self.get_connecting_path(Vector(0, 0), starting_point)
        all_connecting_paths.append(set(start_connecting_path))
        union_of_regions.update(start_connecting_path)

        # walk the now fully connected contiguous region
        path = trace_with_backtracking(union_of_regions, Vector(0, 0))

        # simplify the path for plotter movement
        all_translation_vectors = vectorize_path_processor_func(path)

        return PlotterInstruction(all_translation_vectors, path, regions, all_connecting_paths, all_region_outlines)

    @staticmethod
    def get_connecting_path(start : Vector, end : Vector) -> List[Vector]:
        x1, y1 = start.x, start.y
        x2, y2 = end.x, end.y
        result = []
        # Walk horizontally from x1 to x2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            result.append(Vector(x, y1))

        # Walk vertically from y1 to y2 at x2 (end of horizontal walk)
        for y in range(min(y1, y2), max(y1, y2) + 1):
            result.append(Vector(x2, y))

        return result

    @staticmethod
    def get_nearest_point(region: set[Vector], origin=Vector(0, 0)):
        min_dist = numpy.inf
        nearest_point = Vector(0, 0)
        for p1 in region:
            dist = p1.dist(origin)
            if dist < min_dist:
                min_dist = dist
                nearest_point = p1
        return nearest_point