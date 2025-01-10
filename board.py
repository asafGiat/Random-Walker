from walker import *
from obstacle import *
from portal import *
from statistics import *
from typing import Optional, Any
import math

SCREEN_SIZE = 8
STATISTICS_FILE_PATH = "stats.json"

LOCATION_KEY = 'location'
SIZE_KEY = 'size'


class Board:
    """
    Manages the game board for a simulation, handling the placement and interaction of walkers, obstacles,
    and portals. This class is responsible for executing movements, detecting collisions, and managing
    portal transportation. It maintains the state of various game elements and updates their positions
    based on the simulation rules.

    Attributes:
        __walker (Walker): The entity that moves around the board according to user inputs or predefined behaviors.
        __obstacles (list[Obstacle]): A list of obstacles placed on the board that the walker may encounter.
        __portales (list[Portal]): A list of portals that can transport the walker to different locations on the board.
        __stats (Statistics): Tracks and records various statistics throughout the course of the simulation.
    """

    def __init__(self, walker: Walker):
        self.__walker = walker
        self.__obstacles: list[Obstacle] = []
        self.__portales: list[Portal] = []
        self.__stats = Statistics(STATISTICS_FILE_PATH)

    def add_obstacle(self, obstacle: Obstacle) -> None:
        """public method to add given obstacle"""
        self.__obstacles.append(obstacle)

    def add_portal(self, portal: Portal) -> None:
        """public method to add given portal"""
        self.__portales.append(portal)

    def __if_segment_passed_obstacle(self, src_position: Position, dst_position: Position) -> Optional[Obstacle]:
        """
        explanation about the method by which we decide if the walker is on the obstacle or not.
        first, we do not calculate the size that is on the screen, because it is only a presentation
        we calculate according to the size of the obstacle
        but the walker itself is only on one specific cord, and the red dot is just to visualise it
        that's why we check the distance between the two centers. and if it's smaller than size we return true
        :param src_position: the beginning of the segment to check
        :param dst_position: the end of the segment to check
        :return: the Obstacle the segment passed if it passed one, None if not
        """

        for i in self.__obstacles:
            closest_point = self.__closest_point_on_segment(*src_position, *dst_position, *i.position)
            if self.__distance(*closest_point, *i.position) <= i.get_size():
                return i
        return None

    @staticmethod
    def __closest_point_on_segment(sx: float, sy: float, ex: float, ey: float, cx: float, cy: float) -> Position:
        """
        static help function to help with the calculations of distances
        Calculates the closest point on the line segment (sx, sy) -> (ex, ey) to the point (cx, cy).
        """
        # Vector from start to end of the segment
        v_x, v_y = ex - sx, ey - sy
        # Vector from start to circle center
        w_x, w_y = cx - sx, cy - sy
        # Project vector w onto vector v
        c1 = w_x * v_x + w_y * v_y
        if c1 <= 0:
            return sx, sy  # Closest point is the start point
        c2 = v_x * v_x + v_y * v_y
        if c2 <= c1:
            return ex, ey  # Closest point is the end point

        b = c1 / c2
        px = sx + b * v_x
        py = sy + b * v_y
        return px, py

    @staticmethod
    def __distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """return distance between two positions"""
        return float(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    def __handle_portal_steps(self, src_position: Position, dst_position: Position) -> list[tuple[Position, Position]]:
        """
        Recursively handles the interaction of the walker with portals during a movement step. This method checks
        if the walker starts or ends a step within a portal's radius, allowing for teleportation to the
        portal's corresponding endpoint. It recursively handles sequential portal jumps within a single move.

        :param src_position: The starting position of the walker.
        :param dst_position: The intended ending position of the walker.
        :return: A list of positions detailing the walker's journey, potentially modified by portal transport.

        This method first checks if the walker is already inside a portal to prevent re-triggering transport on
        the same step. If the walker crosses into another portal's radius during the movement, it transports the
        walker, recalculates the step from the new position, and checks for additional portal interactions recursively.
        """
        for portal in self.__portales:
            for endpoint in portal.get_endpoints():
                if self.__distance(*src_position, *endpoint) <= portal.get_size():
                    # means that the step has started allready in the portal,
                    # so we want to ignore it so he will be able to go out
                    continue
                closest_point = self.__closest_point_on_segment(*src_position, *dst_position, *endpoint)
                if self.__distance(*closest_point, *endpoint) <= portal.get_size():
                    self.__walker.set_position(
                        src_position)  # we have to take it back so the walker can recalculate the step
                    self.__walker.portal_walk(dst_position, closest_point, portal.transport(endpoint))
                    # we will use recursion so we will check allso at the other side if the portal if he went through another portal
                    return [(src_position, closest_point)] + self.__handle_portal_steps(portal.transport(endpoint),
                                                                                        self.__walker.get_position())
        return [(src_position, dst_position)]

    def do_move(self) -> bool:
        """
        Executes a movement step for the walker, handling interactions with portals and obstacles. The method
        tries to move the walker and checks if the movement passes through a portal or collides with an obstacle.
        If a collision occurs, the walker's position is reset to the previous position and the move is retried.

        :return: A boolean indicating if the movement was successful without being blocked by too many obstacles.

        This method continuously attempts to move the walker until it can do so without encountering an obstacle
        immediately after a portal. If too many retries occur (indicated by catching an exception), it returns False,
        signaling that the path is blocked.
        """
        # because we don't want it to fall if the obs is after the portal, and we also want to check after the portal
        # if there is an obstacle.
        try:
            while True:
                prev_position = self.__walker.get_position()
                self.__walker.walk()
                cut_moves = self.__handle_portal_steps(prev_position, self.__walker.get_position())
                if not self.__if_cut_step_passed_obstacle(cut_moves):
                    break
                self.__walker.set_position(prev_position)
        except:
            print("too many obstacles, cant pass")
            return False
        self.__stats.record_step(self.__walker.get_position())
        return True

    def __if_cut_step_passed_obstacle(self, cut_step: list[tuple[Position, Position]]) -> bool:
        """check if any part of the list passed an obstacle"""
        for segment in cut_step:
            if self.__if_segment_passed_obstacle(*segment):
                return True
        return False

    def reset_game(self) -> None:
        """resets the board"""
        self.__walker.set_position((0, 0))
        self.__stats.reset_statistics()

    @staticmethod
    def __get_screen_position(location: float) -> int:
        """
        Calculates the screen index for a given location. The screen is divided into units
        defined by SCREEN_SIZE. This method adjusts the location by half of SCREEN_SIZE to
        center the coordinates, then calculates the index by integer division of SCREEN_SIZE.

        :param location: The location in the coordinate system of the simulation.
        :return: The screen index where this location falls.
        """
        return int((location + SCREEN_SIZE / 2) // SCREEN_SIZE)

    @staticmethod
    def __get_location_on_screen(location: float, screen: int) -> float:
        """returns the position of an object on the given screen, given its general position"""
        return location - (screen * SCREEN_SIZE - SCREEN_SIZE / 2)

    def get_screen(self) -> dict[str, Any]:
        """
        this function returns a dictionary containing the information needed for the
        simulation to present
        :return:
        a dictionary with the following arguments:
        s - the location of the screen the walker is in
        w - the location of the walker on the board
        o - obstacles on screen
        p - portals on screen
        """
        ret: dict[str, Any] = {}
        # we will calculate what is the screen that we are returning
        x_screen = self.__get_screen_position(self.__walker.get_position()[X_INDEX])
        y_screen = self.__get_screen_position(self.__walker.get_position()[Y_INDEX])
        ret.update({"s": (x_screen, y_screen)})

        x_on_screen = self.__get_location_on_screen(self.__walker.get_position()[X_INDEX], x_screen)
        y_on_screen = self.__get_location_on_screen(self.__walker.get_position()[Y_INDEX], y_screen)
        ret.update({"w": (x_on_screen, y_on_screen)})

        # Add obstacles that are on the current screen
        screen_obstacles = self.__get_obstacles_on_screen_locations(x_screen, y_screen)
        ret.update({"o": screen_obstacles})

        screen_portals = self.__get_portals_on_screen_locations(x_screen, y_screen)
        ret.update({"p": screen_portals})

        return ret

    def __get_obstacles_on_screen_locations(self, x_screen: int, y_screen: int) -> list[dict[str, Any]]:
        """
        Retrieves a list of obstacles that are located within the current screen bounds. The method calculates
        the screen's boundaries based on the provided screen indexes and SCREEN_SIZE, then filters obstacles
        that fall within these bounds. It returns a list of dictionaries detailing each obstacle's location
        and size on the screen.

        :param x_screen: The horizontal screen index.
        :param y_screen: The vertical screen index.
        :return: A list containing dictionaries for each obstacle visible on the current screen, with keys for
                 'location' (tuple of x, y coordinates) and 'size'.
        """
        screen_obstacles = []
        screen_x_start = x_screen * SCREEN_SIZE - SCREEN_SIZE / 2
        screen_x_end = screen_x_start + SCREEN_SIZE
        screen_y_start = y_screen * SCREEN_SIZE - SCREEN_SIZE / 2
        screen_y_end = screen_y_start + SCREEN_SIZE

        for obstacle in self.__obstacles:
            obs_x = obstacle.position[X_INDEX]
            obs_y = obstacle.position[Y_INDEX]
            if screen_x_start <= obs_x < screen_x_end and screen_y_start <= obs_y < screen_y_end:
                obs_x_on_screen = self.__get_location_on_screen(obs_x, x_screen)
                obs_y_on_screen = self.__get_location_on_screen(obs_y, y_screen)
                obstacle_dict = {"location": (obs_x_on_screen, obs_y_on_screen),
                                 "size": obstacle.get_size()}
                screen_obstacles.append(obstacle_dict)
        return screen_obstacles

    def __get_portals_on_screen_locations(self, x_screen: int, y_screen: int) -> list[dict[str, Any]]:
        """
        Retrieves a list of endpoints that are visible within the current screen boundaries. The method calculates
        the boundaries using the provided screen indices and SCREEN_SIZE. It checks each endpoint of every portal
        to see if it falls within these boundaries and returns a list of dictionaries with each portal's screen
        location and size.

        :param x_screen: The horizontal screen index indicating which screen section to check.
        :param y_screen: The vertical screen index indicating which screen section to check.
        :return: A list containing dictionaries for each visible portal, detailing the 'location' (x, y coordinates)
                 and 'size' of the portals.
        """
        screen_portals = []
        screen_x_start = x_screen * SCREEN_SIZE - SCREEN_SIZE / 2
        screen_x_end = screen_x_start + SCREEN_SIZE
        screen_y_start = y_screen * SCREEN_SIZE - SCREEN_SIZE / 2
        screen_y_end = screen_y_start + SCREEN_SIZE

        for portal in self.__portales:
            for endp in portal.get_endpoints():
                endp_x = endp[X_INDEX]
                endp_y = endp[Y_INDEX]
                if screen_x_start <= endp_x < screen_x_end and screen_y_start <= endp_y < screen_y_end:
                    endp_x_on_screen = self.__get_location_on_screen(endp_x, x_screen)
                    endp_y_on_screen = self.__get_location_on_screen(endp_y, y_screen)
                    portal_data = {"location": (endp_x_on_screen, endp_y_on_screen),
                                   "size": portal.get_size()}
                    screen_portals.append(portal_data)
        return screen_portals

    def set_walking_method(self, meathod: int) -> None:
        """public method to set the walking method of the walker"""
        self.__walker.set_walking_method(meathod)

    def get_walking_method(self) -> int:
        """public method to retrieve the walking method of the walker"""
        return self.__walker.walking_method()
