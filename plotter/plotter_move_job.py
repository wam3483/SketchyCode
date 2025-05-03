import logging

from plotter.path_datatype import VectorPath
from plotter.xy_plotter import XYPlotter


class PlotterMoveJob:
    def __init__(self, plotter : XYPlotter, vector_path : VectorPath):
        self.vector_path = vector_path
        self._plotter = plotter

    def run(self):
        logging.info(f"begin job : {self}")
        for vector in self.vector_path:
            self._plotter.move(vector)
        logging.info(f"end job : {self}")

class PlotterMoveToOrigin:
    def __init__(self, plotter : XYPlotter):
        self._plotter = plotter

    def run(self):
        self._plotter.move_to_origin()

class PlotterClearScreen:
    def __init__(self, plotter : XYPlotter):
        self._plotter = plotter

    def run(self):
        self._plotter.move_to_origin()