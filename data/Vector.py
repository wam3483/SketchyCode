class Vector:
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y

    def dist(self, v2 : 'Vector'):
        dx = abs(self.x - v2.x)
        dy = abs(self.y - v2.y)
        return dx + dy

    def __eq__(self, other):
        return isinstance(other, Vector) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"

def dist(v1 : 'Vector', v2 : 'Vector'):
    dx = abs(v1.x - v2.x)
    dy = abs(v1.y - v2.y)
    return dx + dy