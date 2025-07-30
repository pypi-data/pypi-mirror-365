"""Module for data visualization"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget


def create_boxplots(filepaths, labels, axs, selected_option_numbers):
    """
    Creates boxplots for selected data columns.

    Args:
        filepaths (list): List of file paths to data files.
        labels (list): Corresponding labels for each plot.
        axs (list): List of axes for subplots.
        selected_option_numbers (list): Selected data column names.
    """
    for i, file_path in enumerate(filepaths):
        data_frame = pd.read_csv(file_path)
        filtered_columns = [col for col in selected_option_numbers if
                            col in data_frame.columns]

        if not filtered_columns:
            print(f"Warning: No selected columns found in {file_path}")
            continue

        axs[i].boxplot(
            [data_frame[col].dropna() for col in filtered_columns],
            showfliers=False)
        axs[i].set_xlabel('Wafer', fontsize=16)
        axs[i].set_ylabel(labels[i], fontsize=16)
        axs[i].set_xticklabels(filtered_columns)

    plt.tight_layout()


class PlotFunctions(QWidget):
    """
    A class for handling plotting functionalities, including
    wafer mapping and boxplot creation.

    Attributes:
        master: Reference to the main application.
        button_frame: UI element containing user inputs for plot settings.
    """

    def __init__(self, master, button_frame):
        super().__init__()
        self.master = master
        self.data_frame = None
        self.button_frame = button_frame
        self.step = None
        self.wafer_size = None
        self.edge_exclusion = None

    def plot_raman(self, dirname, ax, numbers_str, parameters, input):
        """
        Generates a WDXRF mapping plot and displays it on the given axis.

        Args:
            dirname (str): Path to the main directory.
            ax (matplotlib.axis): Axis object to plot the data.
            numbers_str (str): Identifier for the data subset.
            parameters (dict): Dictionary of plot parameters.
            input (dict): Input values for wafer size and edge exclusion.
        """
        # File paths and parameters
        subdir = os.path.join(dirname, f"{numbers_str}")
        filename_grid = parameters["Filename"] + "_grid_df.csv"
        filename_boxplot = "Boxplot_" + parameters["Filename"] + ".csv"
        min_value = parameters.get("Min")
        max_value = parameters.get("Max")


        if min_value == "" or min_value is None:
            min_value = None  # or some default value
        else:
            try:
                min_value = float(min_value)
            except ValueError:
                min_value = None  # or some default value
                print(f"Invalid Min value: {min_value}, using default.")

        if max_value == "" or max_value is None:
            max_value = None  # or some default value
        else:
            try:
                max_value = float(max_value)
            except ValueError:
                max_value = None  # or some default value
                print(f"Invalid Max value: {max_value}, using default.")

        # Load boxplot data and scale settings
        filepath_boxplot = os.path.join(dirname, "Liste_data", filename_boxplot)
        filepath_grid = os.path.join(subdir, filename_grid)
        scale_type = self.button_frame.get_values().get('Scale Type', None)

        self.wafer_size = float(input.get("Wafer Size", 0))
        self.edge_exclusion = float(input.get("Edge Exclusion", 0))
        self.step = 0.5
        radius = self.wafer_size / 2

        if scale_type in ['Identical scale', 'Autoscale']:
            pass  # Min and max values are already set from parameters
        elif scale_type == 'Identical scale auto':
            data_frame = pd.read_csv(filepath_boxplot)
            max_value = data_frame.iloc[:, 1:].max().max()
            min_value = data_frame.iloc[:, 1:].min().min()
            print(f"Updated Min: {min_value}, Max: {max_value}")

        # Plot grid data if available
        if os.path.exists(filepath_grid):
            data_frame = pd.read_csv(filepath_grid, index_col=0, header=0)
            if len(data_frame) < 2:
                self._empty_plot(ax, radius)
            else:
                self._plot_grid(ax, data_frame, radius, min_value, max_value,
                                scale_type)
        else:
            self._empty_plot(ax, radius)

    def _empty_plot(self, ax, radius):
        """Creates an empty plot with a placeholder message."""
        ax.text(0, 0, "No data available :(", fontsize=10, color='red',
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.5))
        ax.set_xlim(-radius, radius)
        ax.set_ylim(-radius, radius)
        ax.set_aspect('equal')

    def _plot_grid(self, ax, data_frame, radius, min_value, max_value,
                   scale_type):
        """Plots the grid data with masking and color scaling."""
        x_min, x_max = float(data_frame.columns[0]), float(
            data_frame.columns[-1])
        y_min, y_max = float(data_frame.index[0]), float(data_frame.index[-1])

        X, Y = np.meshgrid(data_frame.columns.astype(float),
                           data_frame.index.astype(float))
        mask = X ** 2 + Y ** 2 >= (radius - self.edge_exclusion) ** 2
        data_frame = data_frame.mask(mask)

        plot = ax.imshow(data_frame, extent=[x_min, x_max, y_max, y_min],
                         cmap='Spectral_r',
                         vmin=min_value if scale_type in ["Identical scale",
                                                              "Identical scale auto"] else None,
                         vmax=max_value if scale_type in [
                             "Identical scale",
                             "Identical scale auto"] else None
                         )
        cbar = plt.colorbar(plot, ax=ax, shrink=0.7)
        cbar.ax.tick_params(labelsize=16)
        # Add wafer boundary
        circle = plt.Circle((0, 0), radius - self.edge_exclusion,
                            color='black', fill=False, linewidth=0.5)
        ax.add_patch(circle)
        ax.set_xlim(-radius, radius)
        ax.set_ylim(-radius, radius)
        ax.set_aspect('equal')  # Assure un rapport d'échelle égal
