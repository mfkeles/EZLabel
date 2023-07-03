import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import pickle
import numpy as np

class DraggableLine:
    def __init__(self, line):
        self.line = line
        self.press = None
        self.connections = []
        self.connections.append(line.figure.canvas.mpl_connect('button_press_event', self.on_press))
        self.connections.append(line.figure.canvas.mpl_connect('button_release_event', self.on_release))
        self.connections.append(line.figure.canvas.mpl_connect('motion_notify_event', self.on_motion))

    def on_press(self, event):
        if event.inaxes != self.line.axes:
            return

        contains, _ = self.line.contains(event)
        if not contains:
            return

        self.press = self.line.get_xdata(), event.xdata

    def on_motion(self, event):
        if self.press is None:
            return

        line_xdata, eventpress_xdata = self.press
        dx = event.xdata - eventpress_xdata
        self.line.set_xdata(line_xdata + dx)
        self.line.figure.canvas.draw()

    def on_release(self, event):
        self.press = None
        self.line.figure.canvas.draw()

    def disconnect(self):
        if self.line is not None and self.line.figure is not None and self.line.figure.canvas is not None:
            for connection in self.connections:
                self.line.figure.canvas.mpl_disconnect(connection)


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.data = None  # To store the loaded data
        self.figure = Figure(figsize=(5, 4), dpi=100)  # The Figure object for the plot
        self.window_size = 45
        self.window_start = None
        self.window_end = None
        self.draggable_start = None
        self.draggable_end = None
        self.ax = None

        # Create the dropdowns
        self.key_var = tk.StringVar(self)
        self.key_var.trace('w', self.update_rows_range)  # Add callback for when the selected key changes
        self.column_var = tk.StringVar(self)
        self.column_var.trace('w', self.update_plot)  # Update plot when selected column changes
        self.key_dropdown = tk.OptionMenu(self, self.key_var, [])
        self.column_dropdown = tk.OptionMenu(self, self.column_var, [])
        self.key_dropdown.pack()
        self.column_dropdown.pack()

        # Create the Spinbox for the row index
        self.row_index_var = tk.StringVar(self)  # Create a StringVar for the Spinbox
        self.row_index_var.trace('w', self.update_plot)  # Update plot when selected row changes
        self.row_index = tk.Spinbox(self, textvariable=self.row_index_var, from_=0, to=0)
        self.row_index.pack()

        # Create the canvas for the plot
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create the button
        self.button = tk.Button(self, text="Load data", command=self.load_data)
        self.button.pack()

        self.window_visible = False

    def show_window(self):
        if self.window_visible:
            if self.draggable_start is not None:
                self.draggable_start.disconnect()
                self.draggable_end.disconnect()
            if self.window_start is not None:
                self.window_start.remove()
            if self.window_end is not None:
                self.window_end.remove()

        self.window_start = self.ax.axvline(x=0, color='r')
        self.window_end = self.ax.axvline(x=self.window_size, color='r')
        self.draggable_start = DraggableLine(self.window_start)
        self.draggable_end = DraggableLine(self.window_end)
        self.canvas.draw()
        self.window_visible = True

    def update_rows_range(self, *args):
        if self.data is not None:  # Check if data has been loaded
            key = self.key_var.get()
            self.row_index.config(to=len(self.data[key]) - 1)
            self.row_index_var.set('0')  # Set the Spinbox value to 0

    def load_data(self):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'rb') as file:
            self.data = pickle.load(file)

        # Update the dropdowns with the keys and columns
        keys = list(self.data.keys())
        columns = [col for col in list(self.data[keys[0]].columns) if col not in ['start_index', 'stop_index', 'region']]
        self.key_dropdown["menu"].delete(0, "end")
        self.column_dropdown["menu"].delete(0, "end")
        for key in keys:
            self.key_dropdown["menu"].add_command(label=key, command=tk._setit(self.key_var, key))
        for column in columns:
            self.column_dropdown["menu"].add_command(label=column, command=tk._setit(self.column_var, column))

        # Set initial values for the dropdowns
        self.key_var.set(keys[0])
        self.column_var.set(columns[0])

        # Update Spinbox range
        self.row_index.config(to=len(self.data[keys[0]]) - 1)  # Set the range of the Spinbox
        self.row_index_var.set('0')  # Set the Spinbox value to 0
        self.update_idletasks()  # Force Spinbox to update

        self.button_show_window = tk.Button(self, text="Show window", command=self.show_window)
        self.button_show_window.pack()

    def update_plot(self, *args):
        key = self.key_var.get()
        column = self.column_var.get()

        if column:
            df = self.data[key]
            try:
                row_idx = int(self.row_index.get())
            except ValueError:
                row_idx = 0

            # Disconnect draggable lines and clear figure and axes if lines exist
            if self.draggable_start is not None:
                self.draggable_start.disconnect()
                self.draggable_end.disconnect()
            if self.ax is not None:
                self.ax.clear()
            else:
                self.ax = self.figure.subplots()

            self.ax.plot(df[column].iloc[row_idx])

            # Adjust x-ticks and x-labels
            self.ax.set_xticks(
                np.arange(0, len(df[column].iloc[row_idx]), step=self.window_size))  # Adjust this as necessary
            self.ax.set_xlabel("Index")

            # If window was previously visible, show it again
            if self.window_visible:
                self.show_window()

            self.canvas.draw()


app = Application()
app.mainloop()
