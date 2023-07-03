import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import pickle

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.data = None  # To store the loaded data
        self.figure = Figure(figsize=(5, 4), dpi=100)  # The Figure object for the plot

        # Create the dropdowns
        self.key_var = tk.StringVar(self)
        self.column_var = tk.StringVar(self)
        self.key_dropdown = tk.OptionMenu(self, self.key_var, [])
        self.column_dropdown = tk.OptionMenu(self, self.column_var, [])
        self.key_dropdown.pack()
        self.column_dropdown.pack()

        # Create the canvas for the plot
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create the button
        self.button = tk.Button(self, text="Load data", command=self.load_data)
        self.button.pack()

    def load_data(self):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'rb') as file:
            self.data = pickle.load(file)

        # Update the dropdowns with the keys and columns
        keys = list(self.data.keys())
        columns = list(self.data[keys[0]].columns)
        self.key_dropdown["menu"].delete(0, "end")
        self.column_dropdown["menu"].delete(0, "end")
        for key in keys:
            self.key_dropdown["menu"].add_command(label=key, command=tk._setit(self.key_var, key))
        for column in columns:
            self.column_dropdown["menu"].add_command(label=column, command=tk._setit(self.column_var, column))

        # Update the plot
        self.update_plot()

    def update_plot(self):
        # Clear the figure
        self.figure.clear()

        # Plot the data
        key = self.key_var.get()
        column = self.column_var.get()
        df = self.data[key]
        ax = self.figure.subplots()
        ax.plot(df[column])

        # Redraw the canvas
        self.canvas.draw()

app = Application()
app.mainloop()
