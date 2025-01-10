import tkinter

import PIL
from board import *
from help_window import *
from settings_window import *
import json
from tkinter import PhotoImage, ttk, messagebox
import tkinter as tk
from PIL import Image, ImageTk, ImageOps, ImageDraw
from typing import Any, Dict, Tuple, List

CANVAS_HEIGHT = 400
CANVAS_WIDTH = 400
SPACE_FOR_CONTROLS = 60
SCREEN_SIZE_IN_PIXELS = "400x360"

WINDOW_DEFAULT_COLOR = "#6724b5"
PORTAL_RING_COLOR = "#f27e0a"
WALKER_DEFAULT_COLOR = "red"
DOT_SIZE = 8

WINDOW_TITLE = "Random Walker"
START_BUTTON_TEXT = "start"
CONTROL_TEXT_COLOR = "white"

CONFIG_PATH = "config.json"
SETTINGS_ICON_PATH = "settings_icon.png"
STONE_WALL_TEXTURE_PATH = "stone2.jpg"
PORTAL_TEXTURE_PATH = "portal.png"
BIDEN_HEAD_TEXTURE_PATH = "biden.png"

class Simulation:
    """
    This class is the top class of the program. the simulator starts by running the show() function
    on a Simulation object
    it manages the graphical user interface and the state of the Random Walker Simulator.
    It initializes the main window, user controls, and the canvas where the simulation is displayed.
    The class is responsible for setting up the UI components, configuring their properties, and handling
    the interactions between the user inputs and the simulation's logic.
    """

    def __init__(self) -> None:
        self.previous_arguments: dict[str, Any] = {}
        self.__obstacles: List[int] = []
        self.__portals: List[int] = []
        self.keep_moving: bool = False  # indicates when to stop and when to go on
        self.reset_screen = False  # to be used after the user changes settings and we want to load them

        self.__init_board()  # important to be called before init window, because the window shows the loaded board
        self.__init_window()

    def __init_window(self) -> None:
        """Initialize the main window using Tkinter."""
        self.window = tk.Tk()
        self.window.title(WINDOW_TITLE)
        # Adjust the window size, needs to contain canvas where the simulation runs, and additional space for controls
        screen_size_str = str(CANVAS_WIDTH) + 'x' + str(CANVAS_HEIGHT + SPACE_FOR_CONTROLS)
        self.window.geometry(screen_size_str)
        # Set the background color
        self.window.configure(bg=WINDOW_DEFAULT_COLOR)

        self.label = tk.Label(self.window, text="random walker simulator", bg=CANVAS_DEFAULT_COLOR,
                              fg=CONTROL_TEXT_COLOR)
        self.label.pack()

        self.__init_control_frame()
        self.__init_canvas()

    def __init_control_frame(self) -> None:
        """this function builds the line of controls on top of the canvas"""
        # Create a frame to hold the buttons in a horizontal layout
        self.__button_frame = tk.Frame(self.window, bg=CANVAS_DEFAULT_COLOR)
        self.__button_frame.pack()

        self.__init_setting_button()
        self.__init_start_button()
        self.__init_help_button()
        self.__init_screen_index_label()
        self.init_walking_method_menu()

    def __init_setting_button(self) -> None:
        """sets a gear icon as settings button"""
        # Load an icon for the settings button
        self.settings_icon = PhotoImage(file=SETTINGS_ICON_PATH)
        self.settings_button = tk.Button(self.__button_frame, image=self.settings_icon,
                                         command=self.__on_click_settings,
                                         bg=CANVAS_DEFAULT_COLOR, borderwidth=1, relief="raised")
        self.settings_button.pack(side=tk.LEFT, padx=5)

    def __init_start_button(self) -> None:
        """sets a button to start the simulation"""
        self.start_button = tk.Button(self.__button_frame, text=START_BUTTON_TEXT, command=self.__on_click_start,
                                      bg=CANVAS_DEFAULT_COLOR,
                                      fg=CONTROL_TEXT_COLOR)
        self.start_button.pack(side=tk.LEFT, padx=5)

    def __init_help_button(self) -> None:
        """sets a button to open the manual for help"""
        self.help_button = tk.Button(self.__button_frame, text="?", command=self.__on_click_help,
                                     bg=CANVAS_DEFAULT_COLOR,
                                     fg=CONTROL_TEXT_COLOR)
        self.help_button.pack(side=tk.LEFT, padx=5)

    def __init_screen_index_label(self) -> None:
        """sets a label to present to the user what part of the screen inifinite surface wee are seeing"""
        self.screen_index_label = tk.Label(self.__button_frame, text="(0,0)", bg=CANVAS_DEFAULT_COLOR,
                                           fg=CONTROL_TEXT_COLOR)
        self.screen_index_label.pack(side=tk.LEFT, padx=5)

    def init_walking_method_menu(self) -> None:
        """sets a dropdown menu for selecting the walking method and changing it while tha simulation is running"""
        self.walking_method_var = tk.StringVar()
        self.walking_method_selector = ttk.Combobox(self.__button_frame, textvariable=self.walking_method_var,
                                                    state="readonly")
        self.walking_method_selector['values'] = list(WALKING_METHODS.keys())
        self.walking_method_selector.current(self.__board.get_walking_method())
        self.walking_method_selector.pack(side=tk.LEFT, padx=5)
        self.walking_method_selector.bind("<<ComboboxSelected>>", self.__change_walking_method)

    def __init_canvas(self) -> None:
        """places the canvas, which is the area that the walker will walk around in"""
        self.canvas = tk.Canvas(self.window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=self.background_color,
                                highlightthickness=0)
        self.canvas.pack()

        self.item_ref: List[PIL.ImageTk.PhotoImage] = []  # needed only so the garbage collector wont erase the pictures
        self.biden_texture = Image.open(BIDEN_HEAD_TEXTURE_PATH)
        # sets the dot initially because every step the simulation erases the previous position and puts it the new one
        self.dot = self.canvas.create_oval(0, 0, 0, 0, fill=self.__walker_color,
                                           outline=WALKER_DEFAULT_COLOR)

        # Load the obstacles and portals images
        self.stone_texture: PIL.Image.Image = Image.open(STONE_WALL_TEXTURE_PATH)
        self.portal_texture: PIL.Image.Image = Image.open(PORTAL_TEXTURE_PATH)

        self.window.update()  # this line is crucial so the set_screen can retrieve the size to initially place objects
        self.__set_screen()

    def __init_board(self) -> None:
        """initializes the board object that calculates the actual simulation, and gives back the data to present"""
        walker = Walker()
        self.__board = Board(walker)
        self.__load_config(CONFIG_PATH)

    def __load_config(self, filename: str) -> None:
        """loads the settings and the data that is saved in the configuration file, and handles it
        if the files are not saved correctly, we save a deafult value"""
        try:
            file_exists = True
            try:
                with open(filename, 'r') as file:
                    config = json.load(file)
            except FileNotFoundError:
                print("Configuration file not found. Creating a default configuration.")
                config = {}
                file_exists = False

            # Track if the configuration is missing any expected keys
            config_updated = False

            if self.load_game_elements(config):  # if the config was updated in one of the functions
                config_updated = True
            if self.__load_walker_settings(config):
                config_updated = True
            if self.__load_colors(config):
                config_updated = True

            # Save the config back if it was missing keys
            if config_updated or not file_exists:
                with open(filename, 'w') as file:
                    json.dump(config, file, indent=4)
                    print("Configuration file updated with default values.")
        except:
            # reset configuration file
            with open(filename, 'w') as file:
                json.dump("{}", file, indent=4)

    def load_game_elements(self, config: Any) -> bool:
        """
        loads the portals and obsacles
        :param config: the data talen from the configuration file
        :return: whether we changed the data because something wasn't set right or not
        """
        config_updated = False

        # Load obstacles if they exist, otherwise initialize with an empty list
        if 'obstacles' not in config:
            config['obstacles'] = []
            config_updated = True
        for obstacle_data in config['obstacles']:
            x = obstacle_data.get('x', 0)  # Default x coordinate if not specified
            y = obstacle_data.get('y', 0)  # Default y coordinate if not specified
            if 'size' not in obstacle_data:
                obstacle_data['size'] = DEAFULT_OBSTICLE_SIZE
                config_updated = True
            size = obstacle_data.get('size')
            self.__board.add_obstacle(Obstacle(x, y, size))

        # Load portals if they exist, otherwise initialize with an empty list
        if 'portals' not in config:
            config['portals'] = []
            config_updated = True
        for portal_data in config['portals']:
            endpoint1 = (portal_data['endpoint1'].get('x', 0), portal_data['endpoint1'].get('y', 0))
            endpoint2 = (portal_data['endpoint2'].get('x', 0), portal_data['endpoint2'].get('y', 0))
            if 'size' not in portal_data:
                portal_data['size'] = 0.3
                config_updated = True
            size = portal_data.get('size')
            self.__board.add_portal(Portal(endpoint1, endpoint2, size))

        return config_updated

    def __load_walker_settings(self, config: Any) -> bool:
        """
        loads the walker speed and the walking method to start in
        :param config: the data taken from the configuration file
        :return:  whether we changed the data because something wasn't set right or not
        """
        config_updated = False

        # Load walking method if it exists, otherwise use a default value
        if 'walk_method' not in config:
            config['walk_method'] = SIMPLE_WALK
            config_updated = True
        self.__board.set_walking_method(config['walk_method'])

        # Load the speed attribute
        if 'speed' not in config:
            config['speed'] = "500"
            config_updated = True
        self.__speed = int(config['speed'])

        return config_updated

    def __load_colors(self, config: Any) -> bool:
        """
        loads the colors and visualising settings of the simulation
        :param config: the data taken from the configuration file
        :return:  whether we changed the data because something wasn't set right or not
        """
        config_updated = False

        if self.__load_use_images(config):
            config_updated = True

        if 'background_color' not in config or not self.__is_valid_color(config['background_color']):
            config['background_color'] = CANVAS_DEFAULT_COLOR
            config_updated = True
        self.background_color = config['background_color']

        if 'walker_color' not in config or not self.__is_valid_color(config['walker_color']):
            config['walker_color'] = WALKER_DEFAULT_COLOR
            config_updated = True
        self.__walker_color = config['walker_color']

        if 'obstacle_color' not in config or not self.__is_valid_color(config['obstacle_color']):
            config['obstacle_color'] = OBSTACLE_DEFAULT_COLOR
            config_updated = True
        self.__obstacle_color = config['obstacle_color']

        if 'portal_color' not in config or not self.__is_valid_color(config['portal_color']):
            config['portal_color'] = OBSTACLE_DEFAULT_COLOR
            config_updated = True
        self.__portal_color = config['portal_color']

        return config_updated

    def __load_use_images(self, config: Any) -> bool:
        """
        loads the user choise if to present the elements as images or colored circles
        :param config: the data taken from the configuration file
        :return:  whether we changed the data because something wasn't set right or not
        """
        config_updated = False
        if "obstacle_use_image" not in config:
            config["obstacle_use_image"] = True
            config_updated = True
        self.use_obstacle_image: bool = config["obstacle_use_image"]

        if "portal_use_image" not in config:
            config["portal_use_image"] = True
            config_updated = True
        self.use_portal_image: bool = config["portal_use_image"]

        if "walker_use_image" not in config:
            config["walker_use_image"] = True
            config_updated = True
        self.use_walker_image: bool = config["walker_use_image"]

        return config_updated

    @staticmethod
    def __is_valid_color(color_code: str) -> bool:
        # Simple check for a valid hex color code
        if isinstance(color_code, str) and color_code.startswith('#') and len(color_code) == 7:
            return all(c in '0123456789ABCDEFabcdef' for c in color_code[1:])
        return False

    def __get_position_on_screen(self, position: float, direction: bool) -> int:
        """
        Calculates the absolute position of an object on the screen based on a given relative unit position
        and the direction of measurement (vertical or horizontal). The screen is divided into a number of
        units specified by SCREEN_SIZE. The function computes the pixel position of the object within these units.

        Parameters:
            position (float): The unit position of the object on the screen, where the full screen length
                              is divided into SCREEN_SIZE units.
            direction (bool): A boolean indicating the direction of measurement; `True` for vertical
                              (from bottom to top), `False` for horizontal (from left to right).

        Returns:
            float: The pixel position on the screen. If `direction` is True, the calculation is adjusted from
                   the bottom of the canvas. If `direction` is False, the calculation is adjusted from
                   the left of the canvas.
        """
        if direction:
            length = self.canvas.winfo_height()
            return int(length - (length / SCREEN_SIZE * position))
        else:
            length = self.canvas.winfo_width()
            return int(length / SCREEN_SIZE * position)

    def get__length_on_screen(self, size: float, direction: bool) -> int:
        if direction:
            length = self.canvas.winfo_height()
            return int(length / SCREEN_SIZE * size)
        else:
            length = self.canvas.winfo_width()
            return int(length / SCREEN_SIZE * size)


    def __move_walker(self, location: Position) -> None:
        """
        moves the walker to a new position
        :param location: the new position we want the walker to move to
        """
        new_x, new_y = location
        x_on_screen = self.__get_position_on_screen(new_x, bool(X_INDEX))
        y_on_screen = self.__get_position_on_screen(new_y, bool(Y_INDEX))
        self.canvas.delete(self.dot)  # delete the previous one
        if self.use_walker_image:  # the user decided to see the walker as an image of joe biden's head
            self.dot = self.__place_circular_png((0, 0), DOT_SIZE, self.biden_texture)
            self.canvas.coords(self.dot, x_on_screen, y_on_screen)
        else:  # the walker will be presented as a colored circle
            self.dot = self.canvas.create_oval(0, 0, 0, 0, fill=self.__walker_color,
                                               outline=WALKER_DEFAULT_COLOR)
            self.canvas.coords(self.dot, x_on_screen - DOT_SIZE, y_on_screen - DOT_SIZE, x_on_screen + DOT_SIZE,
                               y_on_screen + DOT_SIZE)

    def remove_all_obstacles(self) -> None:
        """removes all obstacles from board and clears the list"""
        for i in self.__obstacles:
            self.canvas.delete(i)
        self.__obstacles.clear()

    def place_obstacle(self, obs_dict: dict[str, Any]) -> None:
        """
        places a new obstacle on the board according to choise of obstacle is image or color
        :param obs_dict: data about the wanted obstacle. location (key: 'location') and size (key 'size')
        :return:
        """

        location = tuple(obs_dict.get(LOCATION_KEY, (0, 0)))  # Default to (0,0) if not provided
        size = float(obs_dict.get(SIZE_KEY, 0))  # Default to 0 if not provided
        x_on_screen = self.__get_position_on_screen(location[X_INDEX], bool(X_INDEX))
        y_on_screen = self.__get_position_on_screen(location[Y_INDEX], bool(Y_INDEX))
        x_size = self.get__length_on_screen(size, bool(X_INDEX))
        y_size = self.get__length_on_screen(size, bool(Y_INDEX))
        if self.use_obstacle_image:
            obs_widg = self.__place_jpg((x_on_screen, y_on_screen), x_size, self.stone_texture)
        else:
            obs_widg = self.canvas.create_oval(x_on_screen - x_size, y_on_screen - y_size, x_on_screen + x_size,
                                               y_on_screen + y_size, fill=self.__obstacle_color, outline="blue")
        self.__obstacles.append(obs_widg)

    def __set_obstacles_on_screen(self, obs_data: list[dict[str, Any]]) -> None:
        """
        if there is change is the obstacles to present from the previous turn, remove all the obstacles, and
        replaces the new ones
        :param obs_data: list of dictionaries, each one containing data about an obstacle
        """
        if obs_data == self.previous_arguments.get("o") and not self.reset_screen:
            return
        self.remove_all_obstacles()
        for i in obs_data:
            self.place_obstacle(i)

    def __set_portals_on_screen(self, portals_data: list[dict[str,Any]]) -> None:
        """
        if there is change is the portals to present from the previous turn, remove all the obstacles, and
        replaces the new ones
        :param portals_data: list of dictionaries, each one containing data about a portal
        """
        if portals_data == self.previous_arguments.get("p") and not self.reset_screen:
            return
        self.remove_all_portals()
        for location in portals_data:
            self.place_portal(location)

    def remove_all_portals(self) -> None:
        """removes all portals from board and clears the list"""
        for portal in self.__portals:
            self.canvas.delete(portal)
        self.__portals.clear()

    def place_portal(self, portal_data: dict[str,Any]) -> None:
        """
        places one portal
        :param portal_data: a dictionary conaning data about a portal (size and position)
        """
        location = tuple(portal_data.get(LOCATION_KEY, (0, 0)))
        size = float(portal_data.get(SIZE_KEY, 0))
        x_on_screen = self.__get_position_on_screen(location[X_INDEX], bool(X_INDEX))
        y_on_screen = self.__get_position_on_screen(location[Y_INDEX], bool(Y_INDEX))
        x_size = self.get__length_on_screen(size, bool(X_INDEX))
        y_size = self.get__length_on_screen(size, bool(Y_INDEX))
        if self.use_portal_image:
            portal_widget = self.__place_circular_png((x_on_screen, y_on_screen), x_size, self.portal_texture)
        else:
            portal_widget = self.canvas.create_oval(x_on_screen - x_size, y_on_screen - y_size,
                                                    x_on_screen + x_size, y_on_screen + y_size,
                                                    fill=self.__portal_color, outline=PORTAL_RING_COLOR, width=2)
        self.__portals.append(portal_widget)

    def __start_moving(self) -> None:
        """
        Recursively drives the simulation by scheduling moves and screen updates at intervals defined by __speed.
        Continues moving as long as keep_moving is True.
        """
        try:
            if self.keep_moving:
                if self.__board.do_move():
                    self.__set_screen()  # gets the new data, after the move was done, from the board
                    self.window.after(self.__speed, self.__start_moving)
                else: # board didn't manage to make a move
                    self.__on_click_restart()
        except:
            messagebox.showerror("error", "error accured, restarting")
            self.__on_click_restart()

    def __set_screen(self) -> None:
        """
        Updates the display based on the current state of the board. It sets labels, moves the walker,
        and places obstacles and portals. Ensures the walker dot remains visible by raising its layer.
        """
        args: dict[str, Any] = self.__board.get_screen()  # gets a dictionary with all data needed to set the board
        self._set_screen_label(str(args.get("s")))
        walker_location = tuple[float, float](args.get("w", (0.0, 0.0)))
        self.__move_walker(walker_location)
        obstacles = list(args.get("o", []))
        self.__set_obstacles_on_screen(obstacles)
        portals = list(args.get("p", []))
        self.__set_portals_on_screen(portals)

        self.canvas.tag_raise(self.dot)  # makes the dot in front of other objects.
        self.reset_screen = False  # this is true only one step after settings window was closed, and after we close it
        self.previous_arguments = args  # save the last dictionary so we can compare it

    def _set_screen_label(self, screen_index: str) -> None:
        """sets the label indicating where the walker is on the surface, by the given index"""
        self.screen_index_label.configure(text=screen_index)

    def __on_click_start(self) -> None:
        """called when the user presses the stsrt button. runs the game and changes the button accordingly"""
        self.start_button.configure(text="restart", command=self.__on_click_restart)
        self.keep_moving = True
        self.__start_moving()

    def __on_click_restart(self) -> None:
        """resets the game, and changes the button accordingly"""
        self.keep_moving = False
        self.__init_board()
        self.walking_method_selector.current(self.__board.get_walking_method())
        self.start_button.configure(text="start", command=self.__on_click_start)
        self.__set_screen()

    def __on_click_help(self) -> None:
        """ Handle the help button click """
        help_window = tk.Toplevel(self.window)  # Create a new top-level window
        HelpWindow(help_window)  # Initialize the help window with the new top-level window

    def __on_click_settings(self) -> None:
        """ Handle the settings button click """
        settings_window = tk.Toplevel(self.window)  # Create a new top-level window
        # Initialize the settings window with the new top-level window
        SettingsWindow(settings_window, self.__on_settings_close)

    def __on_settings_close(self) -> None:
        """handles the configuration of settings that were changes when the settings window was open"""
        self.reset_screen = True
        if not self.keep_moving:
            self.__init_board()
            self.__set_screen()
        self.canvas.configure(bg=self.background_color)

    def __change_walking_method(self, event:Any) -> None:
        """ Update the walker's walking method based on the selected option in the dropdown """
        method_name = self.walking_method_var.get()
        method = WALKING_METHODS[method_name]
        self.__board.set_walking_method(method)
        print(f"Changed walking method to {method_name}")

    def __place_jpg(self, position: Position, radius: int, image: PIL.Image.Image) -> int:
        """
        places a picture in given position in given size
        picture is places as circle, and is cropped  from the original jpg in the given size
        :param position: the position to place the image
        :param radius: the size by radios
        :param image: the image needed to be placed
        :return: the placed picture
        """
        x, y = position
        x, y = int(x), int(y)
        radius = int(radius)

        # Crop the image to the size of the obstacle plus a little extra for the border
        cropped_image = image.crop((0, 0, 2 * radius, 2 * radius))

        # Create a mask for the circular area
        mask = Image.new('L', (2 * radius, 2 * radius), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 2 * radius, 2 * radius), fill=255)

        # Apply the mask to the cropped image to create a circular cut-out
        circle_image = ImageOps.fit(cropped_image, mask.size, centering=(0.5, 0.5))
        circle_image.putalpha(mask)

        # Convert the PIL image to a Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(circle_image)

        # Create the canvas image
        item_on_screen = self.canvas.create_image(x, y, image=tk_image, anchor='center')
        # Draw an outer circle border
        # self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline='blue')

        self.item_ref.append(tk_image)

        return int(item_on_screen)

    def __place_circular_png(self, position: Position, radius: int, image: Image.Image) -> int:
        """
        places a picture in given position in given size
        picture is placed as circle, it resizes the entire original png
        :param position: the position to place the image
        :param radius: the size by radios
        :param image: the image needed to be placed
        :return: the placed picture
        """
        x, y = position
        x, y = int(x), int(y)
        radius = int(radius)

        # Resize the image to fit within the specified radius
        resized_image = image.resize((2 * radius, 2 * radius), Image.Resampling.LANCZOS)
        # Convert the PIL image to a Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(resized_image)

        # Create the canvas image
        item_on_screen = self.canvas.create_image(x, y, image=tk_image, anchor='center')
        self.item_ref.append(tk_image)
        return item_on_screen

    def show(self) -> None:
        """public method to stert the simulation"""
        self.window.mainloop()
