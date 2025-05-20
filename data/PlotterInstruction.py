from typing import List, Set

from data import Region
from data.Vector import Vector


class PlotterInstruction:
    def __init__(self, plotter_path : List[Vector], absolute_position_path : List[Vector], regions : List[Region], connecting_paths : List[Set[Vector]], region_outlines : List[Set[Vector]]):
        self.plotter_path = plotter_path
        self.absolute_position_path = absolute_position_path
        self.regions = regions
        self.connecting_paths = connecting_paths
        self.region_outlines = region_outlines