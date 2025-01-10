import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from datetime import datetime
from typing import Callable, Any
import os
import json

from board import STATISTICS_FILE_PATH
from statistics import *
from walker import SIMPLE_WALK, RANDOM_SIZE_WALK, SQUARE_WALK, PREFERRED_WALK

CONFIGURATION_FILE = "config.json"
DEAFULT_OBSTICLE_SIZE = 0.2
DEAFULT_PORTAL_SIZE = 0.3

CANVAS_DEFAULT_COLOR = "#28094d"
OBSTACLE_DEFAULT_COLOR = "black"
PORTAL_COLOR = "#fadd23"
WALKER_DEFAULT_COLOR = "red"

DEFAULT_COLORS = {
    'background_color': CANVAS_DEFAULT_COLOR,
    'obstacle_color': OBSTACLE_DEFAULT_COLOR,
    'portal_color': PORTAL_COLOR,
    'walker_color': WALKER_DEFAULT_COLOR
}

WALKING_METHODS = {
    "Simple Walk": SIMPLE_WALK,
    "Random Size Walk": RANDOM_SIZE_WALK,
    "Square Walk": SQUARE_WALK,
    "Preferred Walk": PREFERRED_WALK
}


class SettingsWindow:
    """
    Manages the configuration settings for the Random Walker simulator, providing an interface for users to
    customize various aspects of the simulation. This class is responsible for initializing and displaying
    setting controls such as color preferences, walking methods, and object display options (image or color).

    The SettingsWindow is organized into tabs for different categories, including Walker, Board, and Statistics,
    allowing users to navigate through settings intuitively. Each tab contains specific controls related to the
    category, ensuring a clean and organized user experience.
    """

    def __init__(self, master: tk.Toplevel, on_close_callback: Callable[[], None]):
        """ Initialize the Settings window with tabs """
        self.load_config()

        self.on_close_callback = on_close_callback  # Store the callback function
        self.master = master
        self.master.title("Settings")
        self.master.geometry("350x560")  # Adjust size as needed
        self.master.configure(bg="#f0f0f0")

        self.__init_tabs()

        # Grab the focus to here, so when other windows pop, for color picking for instance, it will go back here
        self.master.grab_set()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def __init_tabs(self) -> None:
        """creates the tabs for the different settings"""
        self.tab_control = ttk.Notebook(self.master)

        # Create tabs
        self.board_tab = tk.Frame(self.tab_control)
        self.statistics_tab = tk.Frame(self.tab_control)
        self.walker_tab = tk.Frame(self.tab_control)
        self.colors_tab = tk.Frame(self.tab_control)

        # Add tabs to the notebook
        self.tab_control.add(self.board_tab, text='Board')
        self.tab_control.add(self.statistics_tab, text='Statistics')
        self.tab_control.add(self.walker_tab, text='Walker')
        self.tab_control.add(self.colors_tab, text='Colors')

        self.tab_control.pack(expand=1, fill="both")

        # Call methods to populate each tab
        self.create_board_tab()
        self.__create_statistics_tab()
        self.__create_walker_tab()
        self.__create_colors_tab()

    def create_board_tab(self) -> None:
        """ Populate the 'Board' tab with widgets and settings for obstacles and portals """
        # Frame for adding obstacles
        self.board_label = tk.Label(self.board_tab, text="object on board (sets when simulator starts)", padx=10,
                                    pady=10)
        self.board_label.pack()

        self.__add_adding_options()
        self.__add_removing_option()

    def __add_adding_options(self) -> None:
        """add the widgets to add elemenet to the board"""
        self.__add_obstacle_adding_options()
        self.__add_portal_adding_options()

    def __add_obstacle_adding_options(self) -> None:
        """add widgets to add obstacles"""
        self.obstacle_size = tk.DoubleVar(value=DEAFULT_OBSTICLE_SIZE)  # Default size
        obstacle_position_frame = tk.Frame(self.board_tab)
        obstacle_position_frame.pack(fill='x', padx=20, pady=5)

        tk.Label(obstacle_position_frame, text="Add Obstacle (x, y, size):").pack(side=tk.LEFT)
        self.obstacle_x = tk.Entry(obstacle_position_frame, width=5)
        self.obstacle_x.pack(side=tk.LEFT, padx=5)
        self.obstacle_y = tk.Entry(obstacle_position_frame, width=5)
        self.obstacle_y.pack(side=tk.LEFT, padx=5)

        obstacle_size_frame = tk.Frame(self.board_tab)
        obstacle_size_frame.pack(fill='x', padx=20, pady=5)

        # Slider for obstacle size
        self.obstacle_size_slider = tk.Scale(obstacle_size_frame, from_=0.1, to=1.0, resolution=0.1,
                                             orient='horizontal', variable=self.obstacle_size)
        self.obstacle_size_slider.pack(side=tk.LEFT, padx=5)

        self.add_obstacle_button = tk.Button(obstacle_size_frame, text="Add", command=self.add_obstacle)
        self.add_obstacle_button.pack(side=tk.LEFT, padx=10)

    def __add_portal_adding_options(self) -> None:
        """add widgets to add portals"""
        # Frame for adding portals, adjusted for better fit on screen
        portal_frame = tk.Frame(self.board_tab)
        portal_frame.pack(fill='x', padx=20, pady=5)  # Reduced padding for more compact display

        # Labels and entries for portal coordinates split into two lines
        portal_label_frame = tk.Frame(portal_frame)
        portal_label_frame.pack(fill='x')
        tk.Label(portal_label_frame, text="Add Portal (x1, y1, x2, y2, size):").pack(side=tk.LEFT)

        portal_entry_frame = tk.Frame(portal_frame)
        portal_entry_frame.pack(fill='x')
        self.portal_x1 = tk.Entry(portal_entry_frame, width=5)
        self.portal_x1.pack(side=tk.LEFT, padx=3)
        self.portal_y1 = tk.Entry(portal_entry_frame, width=5)
        self.portal_y1.pack(side=tk.LEFT, padx=3)
        self.portal_x2 = tk.Entry(portal_entry_frame, width=5)
        self.portal_x2.pack(side=tk.LEFT, padx=3)
        self.portal_y2 = tk.Entry(portal_entry_frame, width=5)
        self.portal_y2.pack(side=tk.LEFT, padx=3)

        add_frame = tk.Frame(portal_frame)
        add_frame.pack(fill='x')
        self.portal_size = tk.DoubleVar(value=DEAFULT_PORTAL_SIZE)  # Default size
        self.portal_size_slider = tk.Scale(add_frame, from_=0.1, to=1.0, resolution=0.1,
                                           orient='horizontal', variable=self.portal_size)
        self.portal_size_slider.pack(padx=5, side=tk.LEFT)
        self.add_portal_button = tk.Button(add_frame, text="Add", command=self.add_portal)
        self.add_portal_button.pack(side=tk.LEFT, padx=10)

    def __add_removing_option(self) -> None:
        """adds a list of the elements, and an option to remove them"""
        # Add a Treeview to display obstacles and portals
        self.tree = ttk.Treeview(self.board_tab, columns=('Type', 'Coordinates', 'Size'), show='headings')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Coordinates', text='Coordinates')
        self.tree.heading('Size', text='Size')
        # Set minimum width for the columns
        self.tree.column('Type', anchor='center', width=100)
        self.tree.column('Coordinates', anchor='center', width=80)
        self.tree.column('Size', anchor='center', width=80)
        self.tree.pack(fill='x', padx=20, pady=0)

        # Populate the treeview with existing data
        self.populate_tree()

        # Delete button for selected item
        self.delete_button = tk.Button(self.board_tab, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(pady=10)

    def populate_tree(self) -> None:
        """ Populate the treeview with existing obstacles and portals """
        for obs in self.config['obstacles']:
            self.tree.insert('', 'end',
                             values=('Obstacle', f"{obs['x']}, {obs['y']}", obs.get('size', DEAFULT_OBSTICLE_SIZE)))
        for portal in self.config['portals']:
            self.tree.insert('', 'end', values=('Portal',
                                                f"{portal['endpoint1']['x']}, {portal['endpoint1']['y']} -> {portal['endpoint2']['x']}, {portal['endpoint2']['y']}",
                                                portal.get('size', DEAFULT_PORTAL_SIZE)))

    def delete_selected(self) -> None:
        """ Delete the selected item from the treeview and update config """
        for selection in self.tree.selection():
            item = self.tree.item(selection)
            values = item['values']
            if values[0] == 'Obstacle':
                x, y = map(float, values[1].split(', '))
                self.config['obstacles'] = [obs for obs in self.config['obstacles'] if
                                            not (obs['x'] == x and obs['y'] == y)]
            elif values[0] == 'Portal':
                coords = values[1].replace(' -> ', ', ').split(', ')
                x1, y1, x2, y2 = map(float, coords)
                self.config['portals'] = [portal for portal in self.config['portals'] if not (
                        portal['endpoint1']['x'] == x1 and portal['endpoint1']['y'] == y1 and portal['endpoint2'][
                    'x'] == x2 and portal['endpoint2']['y'] == y2)]
            self.tree.delete(selection)
        self.save_config()

    def __create_statistics_tab(self) -> None:
        """ Populate the 'Statistics' tab with widgets and settings """
        self.stats_label = tk.Label(self.statistics_tab, text="Statistics Settings", padx=10, pady=10)
        self.stats_label.pack()

        # Add title for graph export section
        self.graph_title_label = tk.Label(self.statistics_tab, text="Export Graph:", padx=10, pady=10)
        self.graph_title_label.pack()

        # Entry field for the file save path
        self.file_path_entry = tk.Entry(self.statistics_tab, width=40)
        self.file_path_entry.pack(pady=10)

        # Button to browse for file save path
        self.browse_button = tk.Button(self.statistics_tab, text="Browse...", command=self.__browse_file)
        self.browse_button.pack()

        # Export button
        self.export_button = tk.Button(self.statistics_tab, text="Export Graph", command=self.__export_graph)
        self.export_button.pack(pady=20)

        # Add more widgets as needed for statistics settings
        self.reset_stats_button = tk.Button(self.statistics_tab, text="Reset Statistics",
                                            command=self.on_click_reset_statistics, padx=5, pady=5)
        self.reset_stats_button.pack(pady=10)

    def __browse_file(self) -> None:
        """ Open a dialog for user to choose a directory """
        directory = filedialog.askdirectory()  # User selects a directory
        if directory:
            self.file_path_entry.delete(0, tk.END)  # Clear existing entry
            self.file_path_entry.insert(0, directory)  # Insert selected directory
            # Ensure focus goes back to the settings window after closing the dialog
            self.master.focus_set()

    def __export_graph(self) -> None:
        """ Trigger the graph export function with automatic filename generation """
        stats = Statistics(STATISTICS_FILE_PATH)
        directory = self.file_path_entry.get()
        if directory:
            # Generate a filename based on current date and time
            filename = f"random_walk_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path: str = os.path.join(directory, filename)  # Combine directory and filename

            print("Exporting graph to:", file_path)
            stats.make_graph(file_path)

        else:
            print("No directory provided.")

    def add_obstacle(self) -> None:
        """add an obstacle to the configuration file"""
        x_str: str = self.obstacle_x.get()
        y_str: str = self.obstacle_y.get()
        size_str = self.obstacle_size.get()
        try:
            x, y = float(x_str), float(y_str)
            size = float(size_str)
            if not (0.1 <= size <= 1.0):
                raise ValueError("Size must be between 0.1 and 1.0")
            # Check if there is already an obstacle at these coordinates
            if any(obstacle['x'] == x and obstacle['y'] == y for obstacle in self.config['obstacles']):
                tk.messagebox.showerror("Error", "An obstacle already exists at these coordinates.")
                return
            print(f"Adding obstacle at ({x}, {y})")
            print("size: ", size)
            new_obstacle = {"x": x, "y": y, "size": size}
            self.config["obstacles"].append(new_obstacle)
            self.tree.insert('', 'end',
                             values=('Obstacle', f"{new_obstacle['x']}, {new_obstacle['y']}", new_obstacle['size']))
            self.save_config()
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    def add_portal(self) -> None:
        """add a portal to the configuration file"""
        x1_str = self.portal_x1.get()
        y1_str = self.portal_y1.get()
        x2_str = self.portal_x2.get()
        y2_str = self.portal_y2.get()
        size_str = self.portal_size_slider.get()
        # Validate the input to allow negative and decimal numbers for coordinates and ensure size is within range
        try:
            x1, y1, x2, y2 = map(float, [float(x1_str), float(y1_str), float(x2_str),
                                         float(y2_str)])  # Converts inputs to floats
            size = float(size_str)
            if not (0.1 <= size <= 1.0):  # Validate size is within the range
                raise ValueError("Size must be between 0.1 and 1.0")
        except ValueError as e:
            tk.messagebox.showerror("Error", f"Invalid input: {e}")
            return

        # Check if there is already a portal with these endpoints
        if any((portal['endpoint1']['x'] == x1 and portal['endpoint1']['y'] == y1 and
                portal['endpoint2']['x'] == x2 and portal['endpoint2']['y'] == y2) or
               (portal['endpoint1']['x'] == x2 and portal['endpoint1']['y'] == y2 and
                portal['endpoint2']['x'] == x1 and portal['endpoint2']['y'] == y1) for portal in
               self.config['portals']):
            tk.messagebox.showerror("Error", "A portal with these endpoints already exists.")
            return

        # If validation passes, add the portal
        print(f"Adding portal from ({x1}, {y1}) to ({x2}, {y2})")
        new_portal = {
            "endpoint1": {"x": x1, "y": y1},
            "endpoint2": {"x": x2, "y": y2},
            "size": size
        }
        self.config["portals"].append(new_portal)
        self.save_config()

    def load_config(self) -> None:
        """ Load the existing configuration from a JSON file """
        self.config: dict[str, Any] = {}
        try:
            with open(CONFIGURATION_FILE, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = {"walk_method": 0, "obstacles": [], "portals": [], "walker_color": "red"}

    def save_config(self) -> None:
        """ Save the updated configuration back to the JSON file """
        with open(CONFIGURATION_FILE, 'w') as file:
            json.dump(self.config, file, indent=4)

    def __create_walker_tab(self) -> None:
        """ Populate the 'Walker' tab with widgets and settings """
        label = tk.Label(self.walker_tab, text="Walker Settings", padx=10, pady=10)
        label.pack()

        # Walker Speed Setting
        tk.Label(self.walker_tab, text="Set Walking Speed (Interval in ms):", padx=10, pady=2).pack()
        self.speed_scale = tk.Scale(self.walker_tab, from_=1000, to=100, orient='horizontal', resolution=10,
                                    command=self.update_walking_speed)
        self.speed_scale.set(self.config.get('speed', 500))  # Default to 500ms if not set
        self.speed_scale.pack()

        # Walker Color Setting
        tk.Label(self.walker_tab, text="Current Walker Color:", padx=10, pady=2).pack()
        self.color_display = tk.Label(self.walker_tab, text="       ",
                                      bg=str(self.config.get('walker_color', '#FFFFFF')))
        self.color_display.pack(pady=2)

        color_button = tk.Button(self.walker_tab, text="Change Color", command=self.change_walker_color)
        color_button.pack(pady=10)

        # initial walking method
        method_frame = tk.Frame(self.walker_tab)
        method_frame.pack(pady=10)
        tk.Label(method_frame, text=" initial walking method", padx=10, pady=2).pack(anchor='w')
        self.walking_method_var = tk.StringVar()
        self.walking_method_selector = ttk.Combobox(method_frame, textvariable=self.walking_method_var,
                                                    state="readonly")
        self.walking_method_selector['values'] = list(WALKING_METHODS.keys())
        self.walking_method_selector.current(int(self.config['walk_method']))
        self.walking_method_selector.pack(side=tk.LEFT, padx=5)
        self.walking_method_selector.bind("<<ComboboxSelected>>", self.__set_initial_walking_method)

    def update_walking_speed(self, event: Any = None) -> None:
        """ Update the walking speed setting in the configuration """
        self.config['speed'] = self.speed_scale.get()
        self.save_config()
        print("speed changed")

    def change_walker_color(self) -> None:
        """ Open a color picker dialog to select a new color and update the config """
        color_code = colorchooser.askcolor(title="Choose a color")[1]
        if color_code:
            self.config['walker_color'] = color_code
            self.color_display.configure(bg=color_code)
            self.save_config()

    def on_close(self) -> None:
        """Handle the close event by calling the callback function."""
        self.on_close_callback()
        self.master.destroy()

    def __create_colors_tab(self) -> None:
        """ Populate the 'Colors' tab with widgets and settings for background, obstacles, portals, and walker colors """
        label = tk.Label(self.colors_tab, text="Colors configuration, sets on restart", padx=10, pady=10)
        label.pack()

        self.__create_color_option("background_color", "Background Color")
        self.__create_choice_option("obstacle", "Obstacle Display", "Use image for obstacles", "obstacle_color")
        self.__create_choice_option("portal", "Portal Display", "Use image for portals", "portal_color")
        self.__create_choice_option("walker", "Walker Display", "Use image for walker", "walker_color")

        # Add button to reset all colors to defaults
        reset_colors_button = tk.Button(self.colors_tab, text="Reset to Default Colors",
                                        command=self.__reset_to_default_colors)
        reset_colors_button.pack(pady=10)

    def __create_color_option(self, color_key: str, label_text: str) -> None:
        """
        Creates and packs a color option widget within the color settings tab. Each color option consists of a label
        showing the color description, a display label showing the current color, and a button to change the color.

        :param color_key: The key used to identify and retrieve the color setting from the configuration.
        :param label_text: The text that describes the color setting visually on the label.
        """
        frame = tk.Frame(self.colors_tab)
        frame.pack(pady=5)

        # Label
        tk.Label(frame, text=label_text).pack(side=tk.LEFT)
        display_label = tk.Label(frame, width=20, bg=str(self.config.get(color_key, DEFAULT_COLORS.get(color_key))))
        display_label.pack(pady=2)

        # Color change button
        color_button = tk.Button(frame, text=f"Change {label_text}",
                                 command=lambda: self.__change_color(color_key, display_label))
        color_button.pack(side=tk.LEFT)

        setattr(self, f"{color_key}_display", display_label)

    def __create_choice_option(self, key: str, label_text: str, checkbutton_text: str, color_key: str) -> None:
        """
        Creates a configurable option in the UI that includes a label, a checkbutton for choosing between using an
        image or a color, and a button for changing the color. This setup allows users to customize how certain
        elements in the simulation are displayed.

        :param key: The configuration key associated with this choice.
        :param label_text: Text for the main label that describes the choice.
        :param checkbutton_text: Text for the checkbutton that toggles between using an image or a color.
        :param color_key: The key used to retrieve and store the color setting from the configuration.
        """
        frame = tk.Frame(self.colors_tab)
        frame.pack(pady=5)

        # Main label
        tk.Label(frame, text=label_text).pack()
        display_label = tk.Label(frame, width=20, bg=str(self.config.get(color_key, DEFAULT_COLORS.get(color_key))))
        display_label.pack(pady=2)

        # Sub-frame for the checkbutton and color button
        controls_frame = tk.Frame(frame)
        controls_frame.pack()

        # Checkbutton for choosing between image or color
        use_image_var = tk.BooleanVar(value=bool(self.config.get(f"{key}_use_image", True)))
        check = tk.Checkbutton(controls_frame, text=checkbutton_text, variable=use_image_var,
                               command=lambda: self.__toggle_image_color(key, use_image_var.get(), color_key))
        check.pack(side=tk.LEFT)

        # Color change button (disabled by default if image is used)
        color_button = tk.Button(controls_frame, text=f"Change {key.capitalize()} Color",
                                 command=lambda: self.__change_color(color_key, display_label))
        color_button.pack(side=tk.LEFT)
        color_button.config(state=tk.DISABLED if use_image_var.get() else tk.NORMAL)

        # Store the button and variable and display for later use
        setattr(self, f"{key}_color_display", display_label)
        setattr(self, f"{key}_use_image_var", use_image_var)
        setattr(self, f"{key}_color_button", color_button)

    def __toggle_image_color(self, key: str, use_image: bool, color_key: str) -> None:
        """ Toggle between using an image or a color for an object """
        button = getattr(self, f"{key}_color_button")
        if use_image:
            button.config(state=tk.DISABLED)
        else:
            button.config(state=tk.NORMAL)
        self.config[f"{key}_use_image"] = use_image
        self.save_config()

    def __change_color(self, color_key: str, display_label: tk.Label) -> None:
        """ Open a color picker dialog to select a new color and update the config and display label """
        color_code = \
        colorchooser.askcolor(title="Choose a color", initialcolor=str(self.config.get(color_key, '#ffffff')))[
            1]
        if color_code:
            self.config[color_key] = color_code
            display_label.configure(bg=str(color_code))
            self.save_config()
        # on purpose no else, because its when he closes without picking a color, we dont want anything to happen

    def __reset_to_default_colors(self) -> None:
        """ Reset all color settings to their default values and update the UI """
        for key, default in DEFAULT_COLORS.items():
            self.config[key] = default
            display_label = getattr(self, f"{key}_display")
            display_label.configure(bg=default)
        self.save_config()
        messagebox.showinfo("Reset Colors", "All colors have been reset to default settings.")

    def __set_initial_walking_method(self, event: Any) -> None:
        meathod = WALKING_METHODS[self.walking_method_var.get()]
        self.config['walk_method'] = meathod
        self.save_config()

    def on_click_reset_statistics(self) -> None:
        s = Statistics(STATISTICS_FILE_PATH)
        s.erase_statistics()
        messagebox.showinfo("reset stats", "statistics file is now empty")

