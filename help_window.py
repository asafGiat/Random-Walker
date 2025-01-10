import tkinter as tk
from tkinter import ttk

MANUAL_PATH = "manual.txt"


class HelpWindow:
    """this class shows a window with a manual for the user
    the manual is taken from a file"""
    def __init__(self, master: tk.Toplevel):
        """ Initialize the Help window """
        self.master = master
        self.master.title("Manual")
        self.master.geometry("500x500")  # Adjust size as needed
        self.master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 10, "bold"))

        self.__create_widgets()

    def __create_widgets(self) -> None:
        """ Create widgets for the help information """
        title_frame = ttk.Frame(self.master, borderwidth=2, relief="groove", padding="3 3 12 12")
        title_frame.pack(padx=10, pady=10, fill="x")

        title_label = ttk.Label(title_frame, text="User Manual", font=("Arial", 18, "bold"), background="#f0f0f0")
        title_label.pack(pady=10, padx=10)

        self.text_frame = ttk.Frame(self.master, padding="3 3 12 12")
        self.text_frame.pack(padx=10, pady=10, expand=True, fill="both")

        self.text = tk.Text(self.text_frame, height=20, width=60, wrap="word", font=("Helvetica", 12))
        self.text.pack(side="left", fill="both", expand=True)
        self.text.insert(tk.END, self.__get_instructions())
        self.text.config(state=tk.DISABLED)  # Make text read-only

        scrollbar = ttk.Scrollbar(self.text_frame, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scrollbar.set)

        self.close_button = ttk.Button(self.master, text="Close", command=self.master.destroy)
        self.close_button.pack(pady=5)

    def __get_instructions(self) -> str:
        """ Returns the instructions to be displayed """
        return self.__read_manual(MANUAL_PATH)

    @staticmethod
    def __read_manual(filename: str) -> str:
        "returns the text from the manual file"
        try:
            with open(filename, 'r') as file:
                manual_text = file.read()
            return manual_text
        except FileNotFoundError:
            return "Manual file not found."


