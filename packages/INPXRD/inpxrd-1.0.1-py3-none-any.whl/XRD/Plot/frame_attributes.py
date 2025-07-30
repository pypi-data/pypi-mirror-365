"""
Module to manage the visualization of the mapping
"""

import os
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtWidgets import (QFrame, QWidget, QLabel, QVBoxLayout, QPushButton, QSizePolicy, QScrollArea)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Plot.utils import create_savebutton, clear_frame, ouvrir_image
from Plot.plot_functions import PlotFunctions, create_boxplots
from Plot.style_plot import plot_button_style


def get_subplot_dimensions(num_wafer):
    """
    Get appropriate dimensions for subplots based on the number of wafers.
    Uses a loop to determine the correct subplot configuration
    up to 26 wafers.
    """
    if num_wafer == 1:
        return 1, 1
    if num_wafer == 2:
        return 1, 2
    for rows in range(1, 8):  # Iterate over the number of rows from 1 to 5
        cols = 2  # Always have 3 columns
        max_wafer_count = rows * cols
        if num_wafer <= max_wafer_count:
            return rows, cols
    return 1, 1  # Default to 1x1 for any number of wafers greater than 26


class PlotFrame(QWidget):
    """
    A class to manage and display frames in the UI, providing functionality
    for plots and saving combined screenshots.
    """

    def __init__(self, layout, button_frame):
        super().__init__()
        self.last_clicked_ax_index = None
        self.canvas_boxplot_width = None
        self.canvas_boxplot_height = None
        self.canvas_width = None
        self.canvas_height = None
        self.points = None
        self.canvas_right_width = None
        self.selected_point_idx = None
        self.wafer_points = None
        self.plot_button = None
        self.image_raman = None
        self.scroll_area = None
        self.frame_right_layout = None
        self.frame_right = None
        self.frame_left_layout = None
        self.frame_left = None
        self.layout = layout
        self.plot_functions = PlotFunctions(layout, button_frame)
        self.button_frame = button_frame
        self.init_ui()

        self.parameters = None
        self.canvas = None
        self.canvas_boxplot = None
        self.dirname = None
        self.ax_wafer = []
        self.fig = None
        self.axs = None
        self.fig_boxplot = None
        self.axs_boxplot = None
        self.selected_options = None
        self.num_wafer_unsorted = None
        self.num_wafer = None

    def init_ui(self):
        """
        Initialize UI components including frames and layout.
        """

        self.frame_left = QFrame()
        self.frame_left.setFrameShape(QFrame.StyledPanel)
        self.frame_left.setStyleSheet("background-color: white;")
        self.frame_left_layout = QVBoxLayout()
        self.frame_left.setLayout(self.frame_left_layout)

        self.frame_right = QFrame()
        self.frame_right.setFrameShape(QFrame.StyledPanel)
        self.frame_right.setStyleSheet("background-color: white;")

        self.frame_right_layout = QVBoxLayout()
        self.frame_right.setLayout(self.frame_right_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.image_raman = QLabel()
        self.image_raman.setFrameShape(QLabel.StyledPanel)
        self.image_raman.setStyleSheet("background-color: white;")
        self.image_raman.setFixedWidth(600)

        create_savebutton(self.layout, self.frame_left, self.frame_right)
        self.layout.addWidget(self.frame_left, 4, 0, 2, 4)
        self.layout.addWidget(self.image_raman, 4, 4, 1, 4)

        self.plot_button = QPushButton("Plot")
        self.plot_button.setStyleSheet(plot_button_style())

        self.plot_button.setMinimumHeight(80)
        self.plot_button.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding)
        self.plot_button.clicked.connect(self.on_plot_button_clicked)
        self.layout.addWidget(self.plot_button, 2, 5, 2, 2)

    def on_plot_button_clicked(self):
        """
        Slot connected to the 'Plot' button click.
        This will call the update_data method with the selected option.
        """

        self.update_data(self.button_frame.get_selected_option())

    def update_data(self, selected_option):
        """
        Update plots based on the selected options and parameters.
        """

        self.canvas_right_width = 450
        self.canvas_width = 1100
        self.canvas_height = 500
        self.frame_right.setFixedWidth(600)
        self.scroll_area.setFixedWidth(600)
        self.scroll_area.setFixedHeight(600)

        self.image_raman = QLabel()
        self.image_raman.setFrameShape(QLabel.StyledPanel)
        self.image_raman.setStyleSheet("background-color: white;")
        self.image_raman.setFixedWidth(600)
        self.layout.addWidget(self.image_raman, 4, 4, 1, 4)

        def plot_points(axis, points, marker, color='black', markersize=10):
            """Trace les points sur un axe."""
            for point in points:
                axis.plot(point[0], point[1], marker, markerfacecolor='white',
                          markeredgecolor=color, markersize=markersize)

        def configure_axis(axis, xlabel, ylabel):
            """Configure axis labels and title."""
            axis.tick_params(axis='both', labelsize=8)
            axis.set_xlabel(xlabel, fontsize=14)
            axis.set_ylabel(ylabel, fontsize=14)

        # Check if canvas_boxplot exists and needs to be deleted
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.deleteLater()
            self.canvas = None

        # Check if canvas_boxplot exists and needs to be deleted
        if hasattr(self,
                   'canvas_boxplot') and self.canvas_boxplot is not None:
            self.canvas_boxplot.deleteLater()
            self.canvas_boxplot = None

        clear_frame(self.frame_left_layout)

        self.wafer_points = {}

        self.selected_options = selected_option
        self.selected_point_idx = None
        self.dirname = self.button_frame.folder_var_changed()
        self.num_wafer_unsorted = self.update_wafer_count(self.selected_options)
        self.num_wafer = len(self.num_wafer_unsorted)
        parameters = self.button_frame.get_selected_image()

        print(self.num_wafer_unsorted, self.selected_options)
        if not self.dirname or not self.selected_options or not parameters:
            self.canvas_right_width = 0
            self.canvas_width = 0
            self.canvas_height = 0
            self.frame_right.setFixedWidth(0)
            self.scroll_area.setFixedWidth(0)
            self.scroll_area.setFixedHeight(0)
            return

        settings, INPUT = self.button_frame.get_table_data()
        print(parameters[0], settings[parameters[0]])

        self.parameters = settings[parameters[0]]
        Ylabel = settings[parameters[0]].get('Ylabel')

        print(f'Settings are {settings[parameters[0]]}')

        print(f"Ylabel is {Ylabel}")

        if not self.num_wafer:
            return

        # Set fixed size in inches
        fig_width, fig_height = 5, 4

        # Determine subplot grid dimensions
        num_rows, num_cols = get_subplot_dimensions(self.num_wafer)

        # Create figure and subplots
        self.fig, self.axs = plt.subplots(num_rows, num_cols, figsize=(
            num_cols * fig_width, num_rows * fig_height))
        self.fig.suptitle(Ylabel, fontsize=20)

        if isinstance(self.axs, np.ndarray):
            self.axs = self.axs.flatten()
        else:
            self.axs = [self.axs]
        print(self.parameters)
        # Plot each wafer's data
        for i, ax in enumerate(self.axs[:self.num_wafer]):
            self.ax_wafer.append((ax, self.num_wafer_unsorted[i]))

            self.plot_functions.plot_raman(self.dirname, ax,
                                           self.num_wafer_unsorted[i],
                                           self.parameters, INPUT)
            configure_axis(ax, 'X (cm)', 'Y (cm)')
            ax.text(0.5, 1.05, f"Wafer {self.num_wafer_unsorted[i]}",
                    fontsize=14, ha='center', transform=ax.transAxes)

            wafer_dir = os.path.join(self.dirname, self.num_wafer_unsorted[i])
            self.points = []

            if os.path.exists(wafer_dir) and os.path.isdir(wafer_dir):
                for file_name in os.listdir(wafer_dir):
                    if file_name.endswith(".txt") and "_" in file_name:
                        try:
                            xi, yi = file_name[:-4].split("_")
                            self.points.append((float(xi), float(yi)))
                        except ValueError:
                            print(f"Skipping invalid file name: {file_name}")

            if self.points:
                plot_points(ax, self.points, marker='o', color='black',
                            markersize=10)

        # Remove any extra subplots
        for ax in self.axs[self.num_wafer:]:
            ax.remove()

        dpi = self.fig.get_dpi()

        # Adjust canvas size based on the figure size and add it to the layout
        self.canvas = FigureCanvas(self.fig)
        self.canvas_width = int(
            num_cols * fig_width * dpi * self.canvas.device_pixel_ratio)
        self.canvas_height = int(
            num_rows * fig_height * dpi * self.canvas.device_pixel_ratio)
        self.canvas.setFixedSize(self.canvas_width, self.canvas_height)
        self.frame_left.layout().addWidget(self.canvas)
        self.canvas.draw()
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Define the fixed size for each sub-figure
        fig_width, fig_height = 5, 3
        num_cols = 1
        num_rows, filepaths, labels = self.get_boxplot_dimensions()
        print(num_rows, filepaths)
        if num_rows == 0:
            return

        # Create figure and subplots
        self.fig_boxplot, self.axs_boxplot = plt.subplots(num_rows, num_cols,
                                                          figsize=(
                                                              num_cols *
                                                              fig_width,
                                                              num_rows *
                                                              fig_height))

        if isinstance(self.axs_boxplot, np.ndarray):
            self.axs_boxplot = self.axs_boxplot.flatten()
        else:
            self.axs_boxplot = [
                self.axs_boxplot]  # Enveloppe unique axe dans une liste

        create_boxplots(filepaths, labels,
                        self.axs_boxplot,
                        self.num_wafer_unsorted)

        # Créer le canvas_boxplot
        self.canvas_boxplot = FigureCanvas(self.fig_boxplot)

        self.canvas_boxplot_width = int(
            num_cols * fig_width * dpi * self.canvas_boxplot.device_pixel_ratio)
        self.canvas_boxplot_height = int(
            num_rows * fig_height * dpi *
            self.canvas_boxplot.device_pixel_ratio)
        self.canvas_boxplot.setFixedSize(self.canvas_boxplot_width,
                                         self.canvas_boxplot_height)

        self.frame_right_layout.addWidget(self.canvas_boxplot)
        self.frame_right.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding)
        self.scroll_area.setWidget(self.frame_right)
        self.layout.addWidget(self.scroll_area, 5, 4, 1, 3)

        self.frame_right.update()

        # Verify figure creation
        print(f"self.fig_boxplot "
              f"created with {len(self.fig_boxplot.axes)} axes.")

    def on_click(self, event):
        """
        Handles mouse click events to update the display and highlight the
        closest point on the clicked axis.

        Args:
            event: The event object containing information about the click
            event.
        """

        # Check if the Raman image widget exists; if not, create it
        if not hasattr(self, 'image_raman') or self.image_raman is None:
            self.image_raman = QLabel()
            self.image_raman.setFrameShape(QLabel.StyledPanel)
            self.image_raman.setStyleSheet("background-color: white;")
            self.image_raman.setFixedWidth(600)
            self.image_raman.setFixedHeight(300)
            self.layout.addWidget(self.image_raman, 4, 3, 1, 3)

        # Initialize or retrieve indices of selected points
        if not hasattr(self,
                       "selected_point_idx") or self.selected_point_idx is None:
            self.axs = np.atleast_1d(self.axs)
            self.selected_point_idx = [None] * len(self.axs.flat)

        # Store the last clicked axis index
        if not hasattr(self, "last_clicked_ax_index"):
            self.last_clicked_ax_index = None

        # Ensure the click is on a valid axis
        if event.inaxes:
            wafer_number = None
            for ax, num_wafer in self.ax_wafer:
                if event.inaxes == ax:
                    wafer_number = num_wafer
                    break

            clicked_ax_index = None
            for idx, ax in enumerate(self.axs.flat):
                if event.inaxes == ax:
                    clicked_ax_index = idx
                    break

            if clicked_ax_index is None:
                print("Click outside of recognized axes.")
                return

            # Reset the previously selected point if a different axis was
            # clicked
            if self.last_clicked_ax_index is not None and \
                    self.last_clicked_ax_index != clicked_ax_index:
                prev_idx = self.last_clicked_ax_index
                if self.selected_point_idx[prev_idx] is not None:
                    old_idx = self.selected_point_idx[prev_idx]

                    # Retrieve previous wafer directory and its points
                    wafer_dir = os.path.join(self.dirname,
                                             self.num_wafer_unsorted[prev_idx])
                    points_in_prev_ax = []
                    if os.path.exists(wafer_dir) and os.path.isdir(wafer_dir):
                        for file_name in os.listdir(wafer_dir):
                            if file_name.endswith(".txt") and "_" in file_name:
                                try:
                                    xi, yi = file_name[:-4].split("_")
                                    points_in_prev_ax.append(
                                        (float(xi), float(yi)))
                                except ValueError:
                                    print(
                                        f"Skipping invalid file name: "
                                        f"{file_name}")

                    # Restore the previous point's appearance
                    old_x, old_y = points_in_prev_ax[old_idx]
                    self.axs.flat[prev_idx].plot(
                        [old_x], [old_y], 'o',
                        markerfacecolor='white',
                        markeredgecolor='black',
                        markersize=10
                    )
                    self.selected_point_idx[prev_idx] = None  # Reset index

                    # Refresh only the previous axis
                    self.axs.flat[prev_idx].draw_artist(self.axs.flat[prev_idx])
                    self.canvas.blit(self.axs.flat[prev_idx].bbox)

            # Update the last clicked axis index
            self.last_clicked_ax_index = clicked_ax_index

            # Retrieve points for the clicked axis
            wafer_dir = os.path.join(self.dirname,
                                     self.num_wafer_unsorted[clicked_ax_index])
            points_in_ax = []
            if os.path.exists(wafer_dir) and os.path.isdir(wafer_dir):
                for file_name in os.listdir(wafer_dir):
                    if file_name.endswith(".txt") and "_" in file_name:
                        try:
                            xi, yi = file_name[:-4].split("_")
                            points_in_ax.append((float(xi), float(yi)))
                        except ValueError:
                            print(f"Skipping invalid file name: {file_name}")

            if not points_in_ax:
                print(f"No points found for Axis {clicked_ax_index}.")
                return

            # Get click coordinates
            x_click, y_click = event.xdata, event.ydata

            # Compute the distance from the click position to each point on
            # the axis
            distances = [np.hypot(x - x_click, y - y_click) for x, y in
                         points_in_ax]
            min_dist = min(distances)
            tolerance = 10  # Tolerance to recognize a valid point

            if min_dist <= tolerance:
                closest_point_idx = distances.index(min_dist)
                x, y = points_in_ax[closest_point_idx]

                # Check if a point was previously selected for this axis
                if self.selected_point_idx[clicked_ax_index] is not None:
                    old_idx = self.selected_point_idx[clicked_ax_index]
                    old_x, old_y = points_in_ax[old_idx]

                    # Restore appearance of the previously selected point
                    self.axs.flat[clicked_ax_index].plot(
                        [old_x], [old_y], 'o',
                        markerfacecolor='white',
                        markeredgecolor='black',
                        markersize=10
                    )

                # Update the selected point index
                self.selected_point_idx[clicked_ax_index] = closest_point_idx

                # Highlight the new selected point in yellow
                self.axs.flat[clicked_ax_index].plot(
                    x, y, 'o',
                    markerfacecolor='yellow',
                    markeredgecolor='black',
                    markersize=10
                )

                # Refresh only the affected axis
                self.canvas.blit(self.axs.flat[clicked_ax_index].bbox)
                ouvrir_image(self.dirname, wafer_number, x, y, self.image_raman)
                print(f"Clicked at ({x:.2f}, {y:.2f})")
            else:
                print("Click outside of data points.")

    def get_boxplot_dimensions(self):
        """
        Determine appropriate dimensions for subplots
        based on the selected parameters in self.parameters.
        """

        settings, INPUT = self.button_frame.get_table_data()
        # Initialize variables for valid files and labels
        row_number = 0
        filepaths = []
        labels = []

        # Iterate over parameters to construct filepaths and labels
        for param in settings:
            # Check if the "Boxplot" checkbox is checked
            if param.get("Boxplot",
                         False):  # Only consider rows with "Boxplot" checked
                filename = f"Boxplot_{param['Filename']}.csv"
                ylabel = param["Ylabel"]
                file_path = os.path.join(self.dirname, "Liste_data", filename)

                if os.path.exists(file_path):
                    print(f"The file '{filename}' exists.")
                    row_number += 1
                    filepaths.append(file_path)
                    labels.append(ylabel)
                else:
                    print(f"Warning: The file '{filename}' was not found.")

        return row_number, filepaths, labels

    def update_wafer_count(self, num_wafer_sorted):
        """
        Update the count and sort of selected
        wafers based on the directory structure.
        """
        if os.path.isdir(self.dirname):
            subdirs = [d for d in os.listdir(self.dirname)
                       if os.path.isdir(os.path.join(self.dirname, d))]
            num_wafer_sorted = sorted(set(num_wafer_sorted) & set(subdirs))
            num_wafer_sorted = [str(num) for num in
                                sorted(map(int, num_wafer_sorted))]
        else:
            print(f"Directory does not exist: {self.dirname}")
        return num_wafer_sorted
