from path_datatype import VectorPath
class PlotterJob:
    def __init__(self, vector_path : VectorPath, step_speed : float):
        self.vector_path = vector_path
        self.step_speed = step_speed