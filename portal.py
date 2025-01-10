DEAFULT_PORTAL_SIZE = 0.3

from walker import Position

class Portal:
    """
    Represents a portal in the simulation environment. Portals connect two distinct endpoints, allowing for
    instantaneous transportation between them. Each portal has a fixed size that determines its interaction
    threshold with the walker.
    """
    def __init__(self, endpoint1: Position, endpoint2: Position, size: float = DEAFULT_PORTAL_SIZE):
        self.endpoint1: Position = endpoint1
        self.endpoint2: Position = endpoint2
        self.__size = size

    def get_endpoints(self) -> tuple[Position, Position]:
        """
        Returns both endpoints of the portal.

        :return: A tuple containing both endpoints.
        """
        return (self.endpoint1, self.endpoint2)

    def transport(self, position: Position) -> Position:
        """
        Transports the walker to the corresponding portal endpoint.

        :param position: The current position of the walker.
        :return: The new position of the walker if it enters a portal, otherwise the same position.
        """
        if position == self.endpoint1:
            return self.endpoint2
        elif position == self.endpoint2:
            return self.endpoint1
        return position

    def get_size(self) -> float:
        """returns the size of the portal"""
        return self.__size
