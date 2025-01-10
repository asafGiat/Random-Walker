import random
import math
from typing import Tuple

Position = Tuple[float, float]

X_INDEX = 0
Y_INDEX = 1

SIMPLE_WALK = 0
RANDOM_SIZE_WALK = 1
SQUARE_WALK = 2
PREFERRED_WALK = 3


class Walker:
    """
    Represents a walker within a simulation, capable of moving according to various predefined walking methods.
    This class provides functionality for simple random walking, square grid walking, random-sized steps,
    and preferred walking patterns towards specific directions or back to the origin.

    Attributes:
        __x (float): The current x-coordinate of the walker.
        __y (float): The current y-coordinate of the walker.
        __walking_method (int): The method of walking, which defines the pattern and mechanics of movement.

    Methods:
        walk(): Executes a movement step based on the current walking method.
        portal_walk(): Calculates the walker's new position when encountering a portal during a move.
        get_position(): Returns the current position of the walker as a tuple.
        set_position(): Sets the walker's position to a specified location.
        walking_method(): Retrieves the current walking method.
        set_walking_method(): Sets the walking method, validating against predefined options.

    The walker supports dynamic interaction with environments, such as portals, and offers customizable
    walking patterns, making it versatile for different types of simulations. It maintains its own position
    and can adjust its movement strategy dynamically based on method settings.
    """
    def __init__(self, walking_method: int = SIMPLE_WALK):
        self.__x: float = 0
        self.__y: float = 0
        self.__walking_method = walking_method

    def walk(self) -> None:
        """move the walker one step, according to its current walking method"""
        if self.__walking_method == SIMPLE_WALK:
            self.__simple_walk()
        elif self.__walking_method == SQUARE_WALK:
            self.__square_walk()
        elif self.__walking_method == RANDOM_SIZE_WALK:
            self.__random_size_walk()
        elif self.__walking_method == PREFERRED_WALK:
            self.__preferred_walk()

    def __simple_walk(self) -> None:
        """move one step in any direction"""
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        self.__x += math.cos(angle)  # Change in x
        self.__y += math.sin(angle)  # Change in y

    def __square_walk(self) -> None:
        """move one step in one of the 4 straight directions"""
        direction = random.choice(['x', 'y'])
        if direction == 'x':
            self.__x += random.choice([-1, 1])
        else:
            self.__y += random.choice([-1, 1])

    def __random_size_walk(self) -> None:
        """move to any direction, a size in any length between 0.5 to 1.5"""
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        step_length = random.uniform(0.5, 1.5)  # Random step length between 0.5 and 1.5
        self.__x += math.cos(angle) * step_length  # Change in x
        self.__y += math.sin(angle) * step_length  # Change in y

    def __preferred_walk(self) -> None:
        """move to any direction, but hav a bigger probobility to move to one of the
        4 straigh directions or towards the origin (0,0)"""
        # Local probabilities specific to this method
        base_probability = 1
        preferred_probability = 10  # Higher weight for preferred directions

        # Generate a random angle
        angle = random.uniform(0, 2 * math.pi)
        step_length = 1  # Fixed step length

        # Increase probability for specific angles corresponding to up, down, left, right, and towards origin
        # Define preferred angles for special directions
        preferred_angles = {
            0: preferred_probability,  # right
            math.pi / 2: preferred_probability,  # up
            math.pi: preferred_probability,  # left
            3 * math.pi / 2: preferred_probability,  # down
            math.atan2(-self.__y, -self.__x): preferred_probability  # towards origin
        }

        # Adjust the angle based on weighted probability
        angles = [angle] + list(preferred_angles.keys())
        weights = [base_probability] + list(preferred_angles.values())
        chosen_angle = random.choices(angles, weights=weights, k=1)[0]

        # Move the walker
        self.__x += math.cos(chosen_angle) * step_length
        self.__y += math.sin(chosen_angle) * step_length

    def portal_walk(self, original_destination: Position, portal_entry: Position, portal_exit: Position) -> None:
        """
        caculates where he landes if he he encountered a portal
        :param original_destination: where he started the step
        :param portal_entry: where he enter the portal
        :param portal_exit: the other endpoint of the portals position
        :return: where the step is supposed to end
        """
        # Calculate the original movement vector
        original_dx = original_destination[X_INDEX] - self.__x
        original_dy = original_destination[Y_INDEX] - self.__y

        # Calculate the part of the step before entering the portal
        entry_dx = portal_entry[X_INDEX] - self.__x
        entry_dy = portal_entry[Y_INDEX] - self.__y

        # Calculate the remaining part of the step after exiting the portal
        # Using vector scaling based on the ratio of distances
        step_ratio = math.sqrt((entry_dx ** 2 + entry_dy ** 2) / (original_dx ** 2 + original_dy ** 2))
        remaining_dx = (1 - step_ratio) * original_dx
        remaining_dy = (1 - step_ratio) * original_dy

        # Apply the remaining step from the portal exit point
        self.__x = portal_exit[X_INDEX] + remaining_dx
        self.__y = portal_exit[Y_INDEX] + remaining_dy

    def get_position(self) -> Position:
        """return the cuurent posision of the walker"""
        return self.__x, self.__y

    def set_position(self, new_position: Position) -> None:
        """move the walker to another position"""
        self.__x = new_position[X_INDEX]
        self.__y = new_position[Y_INDEX]

    def walking_method(self) -> int:
        """get the current walking meathod"""
        return self.__walking_method

    def set_walking_method(self, method: int) -> None:
        """change the walking method"""
        if method in [SIMPLE_WALK, RANDOM_SIZE_WALK, SQUARE_WALK, PREFERRED_WALK]:
            self.__walking_method = method
        else:
            raise ValueError("Invalid walking method")
