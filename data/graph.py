from typing import Generic, TypeVar, Dict, Callable, List, Tuple

T = TypeVar('T')

class Graph(Generic[T]):

    def __init__(self):
        self.graph : Dict[T, list[T]] = {}

    def add_vertex(self, vertex1 : T) -> List[T]:
        if vertex1 not in self.graph:
            self.graph[vertex1] = []
        return self.graph[vertex1]

    def connect(self, vertex1 : T, vertex2 : T, bi_directional : bool = True):
        v1_list = self.add_vertex(vertex1)
        v1_list.append(vertex2)

        if bi_directional:
            v2_list = self.add_vertex(vertex2)
            v2_list.append(vertex1)

    @staticmethod
    def traveling_salesman_graph(
            vertices: List[T],
            distance_func: Callable[[T, T], float]
    ) -> 'Graph[T]':
        #Python evaluates annotations at func definition time, but Graph[T] isn't constructed yet inside its own class body.
        # So Python doesn't know what Graph[T] is.
        if not vertices:
            return Graph()

        unvisited = set(vertices)
        path = []
        total_distance = 0.0

        current = vertices[0]
        path.append(current)
        unvisited.remove(current)

        while unvisited:
            next_vertex = min(unvisited, key=lambda v: distance_func(current, v))
            total_distance += distance_func(current, next_vertex)
            current = next_vertex
            path.append(current)
            unvisited.remove(current)

        graph = Graph()
        last_region = None
        for region in path:
            graph.add_vertex(region)
            if last_region is not None:
                graph.connect(last_region, region)
            last_region = region

        return graph