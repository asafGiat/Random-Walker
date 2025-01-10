import json
import os
from math import sqrt
from typing import Union, Any

from walker import Position, X_INDEX, Y_INDEX
import matplotlib.pyplot as plt

BEGINNING_STAGE = 0
POSOTIVE_SIDE = 1
NEGETIVE_SIDE = -1


class Statistics:
    """
    Manages and records statistical data for the Random Walker simulation. This class tracks the walker's movement,
    calculates various metrics such as distance from the origin and number of crossings over the y-axis, and
    monitors when the walker passes a predefined radius threshold. It stores all statistics in a JSON file and
    provides functionality to generate graphical representations of these metrics.

    Attributes:
        file_path (str): Path to the JSON file where statistical data is stored and loaded from.
        turn_count (int): Counter for the number of steps taken by the walker.
        initial_position (tuple[float, float]): The starting position of the walker, used as a reference for distance calculations.
        data (dict): Container for all the statistical data collected during the simulation.
        radius_threshold (int): The distance threshold from the origin at which certain statistics start being recorded.
        has_passed_threshold (bool): Flag to indicate whether the radius threshold has been crossed.
        y_axis_side (int): Indicator of the walker's last position relative to the y-axis to track crossings.
        crossing_count (int): Counter for the number of times the walker crosses the y-axis.

    The class handles the loading and saving of data, updates statistical measurements upon each walker step,
    and can reset statistics for new simulation runs. It also includes methods to visualize data through graphs,
    aiding in the analysis of the walker's behavior over time.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.turn_count = 0
        self.initial_position = (0, 0)  # Assuming starting at origin; update if starting position can change
        self.data = self.load_data()
        self.radius_threshold = 10  # Threshold radius
        self.has_passed_threshold = False  # Track if the threshold has been passed already
        self.y_axis_side: int = BEGINNING_STAGE
        self.crossing_count = 0

    def load_data(self) -> Any:
        """Load data from the JSON file, or initialize if the file does not exist or is empty."""
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                # Ensure all expected keys are present
                data.setdefault("initial_position", list(self.initial_position))
                data.setdefault("average_distance", [])
                data.setdefault("steps_to_pass_radius_10", {"total_counts": 0, "sum_steps": 0, "average_steps": 0})
                return data
        else:
            return {
                "initial_position": list(self.initial_position),
                "average_distance": [],
                "steps_to_pass_radius_10": {
                    "total_counts": 0,
                    "sum_steps": 0,
                    "average_steps": 0
                }
            }

    def record_step(self, position: Position) -> None:
        """Record the position of the walker, update turn count, and calculate distances."""
        self.turn_count += 1
        self.__update_avrage_distance(position)
        self.__update_radius_pass(position)

        # Save the updated data back to the file
        self.save_data()

    def __update_avrage_distance(self, position: Position) -> None:
        """updates the in the stats file the avarage distance to the origin for the current step number"""
        distance = sqrt((position[0] - self.initial_position[0]) ** 2 +
                        (position[1] - self.initial_position[1]) ** 2)

        distance_from_x_axis = abs(position[1] - self.initial_position[1])
        distance_from_y_axis = abs(position[0] - self.initial_position[0])

        # Update average distances
        if len(self.data["average_distance"]) < self.turn_count:
            # First time this step is reached
            self.data["average_distance"].append({
                "count": 1,
                "average_distance": distance,
                "average_x_axis": distance_from_x_axis,
                "average_y_axis": distance_from_y_axis,
                "average_crossing_y": 0
            })
        else:
            # Update existing data
            step_data = self.data["average_distance"][self.turn_count - 1]
            old_count = step_data["count"]
            step_data["count"] += 1

            # Update the overall average distance
            step_data["average_distance"] += (distance - step_data["average_distance"]) / step_data["count"]
            # Update the average distance from the x-axis
            step_data["average_x_axis"] += (distance_from_x_axis - step_data["average_x_axis"]) / step_data["count"]
            # Update the average distance from the y-axis
            step_data["average_y_axis"] += (distance_from_y_axis - step_data["average_y_axis"]) / step_data["count"]

        self.__update_y_crossing_average(position)


    def __update_radius_pass(self, position: Position) -> None:
        """Check and update statistics for passing the threshold radius."""
        distance = sqrt((position[0] - self.initial_position[0]) ** 2 +
                        (position[1] - self.initial_position[1]) ** 2)

        if not self.has_passed_threshold and distance >= self.radius_threshold:
            self.has_passed_threshold = True  # Mark that the threshold has been passed
            steps_to_pass = self.turn_count  # Use turn_count to determine the steps taken to pass the threshold
            radius_stats = self.data["steps_to_pass_radius_10"]
            radius_stats["total_counts"] += 1
            radius_stats["sum_steps"] += steps_to_pass
            radius_stats["average_steps"] = radius_stats["sum_steps"] / radius_stats["total_counts"]

    def __update_y_crossing_average(self, position: Position) -> None:
        """has to be called after average distance"""
        didpass: bool = False
        if self.y_axis_side > 0:
            if position[X_INDEX] < 0:
                didpass = True
                self.y_axis_side = NEGETIVE_SIDE
        elif self.y_axis_side < 0:
            if position[X_INDEX] > 0:
                didpass = True
                self.y_axis_side = POSOTIVE_SIDE
        else:  # its still on the y axis from the begining
            if position[X_INDEX] > 0:
                self.y_axis_side = POSOTIVE_SIDE
            if position[X_INDEX] < 0:
                self.y_axis_side = NEGETIVE_SIDE

        if didpass:
            self.crossing_count += 1

        # upload to data
        step_data = self.data["average_distance"][self.turn_count - 1]
        step_data["average_crossing_y"] += (self.crossing_count - step_data["average_crossing_y"]) / step_data["count"]

    def save_data(self) -> None:
        """Save the statistical data to a JSON file."""
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def reset_statistics(self) -> None:
        """Reset the statistics for a new simulation run."""
        self.has_passed_threshold = False
        self.turn_count = 0  # Reset turn count for accurate tracking in each new simulation



    def make_graph(self, path: str) -> None:
        """Generate and save plots based on the distances and y-axis crossings."""
        # Extract data for plotting
        distances = [step['average_distance'] for step in self.data['average_distance']]
        x_distances = [step['average_x_axis'] for step in self.data['average_distance']]
        y_distances = [step['average_y_axis'] for step in self.data['average_distance']]
        y_crossings = [step.get('average_crossing_y', 0) for step in self.data['average_distance']]

        plt.figure(figsize=(15, 5))

        # Plot average distances
        plt.subplot(1, 3, 1)
        plt.plot(distances, marker='o', linestyle='-', color='b', label='Distance from origin')
        plt.plot(x_distances, marker='o', linestyle='--', color='g', label='X-Axis Distance')
        plt.plot(y_distances, marker='o', linestyle=':', color='r', label='Y-Axis Distance')
        plt.title('Distance Comparisons per Step')
        plt.xlabel('Step Number')
        plt.ylabel('Distance')
        plt.legend(loc='best', shadow=True, fancybox=True)

        # Plot y-axis crossings
        plt.subplot(1, 3, 2)
        plt.plot(y_crossings, marker='o', linestyle='-', color='r')
        plt.title('Y-Axis Crossings per Step')
        plt.xlabel('Step Number')
        plt.ylabel('Crossings')
        plt.ylim(bottom=0)  # Ensure y-axis starts at 0

        # Save the plot to a file or show
        plt.tight_layout()
        plt.savefig(path)  # Adjust path as needed
        plt.close()

    def erase_statistics(self) -> None:
        self.data = {}
        self.save_data()


# no idea why, but these lines make the window in a much better quality. do not remove them!!
a = Statistics("stats.json")
a.make_graph("plot_output.png")
