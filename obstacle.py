from board import Position

class Obstacle:
    """
    Represents an obstacle in the simulation environment.
    An obstacle cant be passed or landed on by the walker
    An obstacle is characterized by its position (x, y) and size.
    The position is defined in the coordinate space of the simulation,
    and the size determines its scale relative to other elements.
    """
    def __init__(self, x: float = 0.0, y: float = 0.0, size: float = 0.2):
        self.__x = x
        self.__y = y
        self.__size = size

    @property
    def position(self) -> Position:
        """Return the current position of the obstacle."""
        return self.__x, self.__y

    def get_size(self) -> float:
        """return the size of an obstacle"""
        return self.__size
