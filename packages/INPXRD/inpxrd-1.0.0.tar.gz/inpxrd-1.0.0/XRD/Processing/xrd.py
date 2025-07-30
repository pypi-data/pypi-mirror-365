"""
This module contains functions and classes for performing XRF spectra fitting.
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from functools import partial
from multiprocessing import Queue
from threading import Thread
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication
from fitspy.core.spectra import Spectra
from fitspy.core.spectra_map import SpectraMap
from fitspy.core.spectrum import Spectrum
from fitspy.core.utils import load_from_json
from fitspy.core.utils_mp import fit_mp
from scipy.interpolate import griddata
import gc

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Layout.settings import SettingsWindow


def plot_wdf_mp(filepath, settings, input, slot_number, identical=None,
                stats=None):
    """
    Processes a single WDF data file and generates mapping plots.

    :param filepath: Path to the WDF file.
    :param settings: List of dictionaries containing 'Peak', 'Ylabel',
    and 'Filename'. Optionally includes thresholds ('Min', 'Max').
    :param input: Dictionary with 'Wafer Size' and 'Edge Exclusion' settings.
    :param slot_number: Optional slot number for labeling plots.
    :param identical: If True, uses a consistent scale for all plots.
    :param stats: If true, add mean and sigma for all plots.
    """
    # Print the file being processed
    print('Processing:', filepath)

    # Determine wafer number and initial step size
    wafer_number = os.path.dirname(filepath)
    step = 0.5

    # Load data from CSV into a Pandas DataFrame
    data_frame = pd.read_csv(filepath)

    # Initialize variables for color scale limits
    vmin = None
    vmax = None
    thr_column = None
    threshold = None

    # Extract peaks, labels, and filenames from settings
    peaks = [s['Peak'].strip() for s in settings if s.get('Peak')]
    ylabels = [s['Ylabel'].strip() for s in settings if s.get('Ylabel')]
    grids = [s['Filename'].strip() for s in settings if s.get('Filename')]
    filenames = [s['Filename'].strip() for s in settings if s.get('Filename')]

    # Modify filenames if identical scaling is enabled
    if identical:
        filenames = [f"{file}_ID_scale" for file in filenames]

    # Identify thresholds for each peak, if applicable
    for i, setting in enumerate(settings):
        if setting.get('Threshold'):
            threshold = int(settings[i]['Min'])
            thr_column = settings[i]['Peak']

    # Extract wafer properties from input
    wafer_size = int(input.get('Wafer Size', 0))
    edge_exclusion = int(input.get('Edge Exclusion', 0))
    radius = wafer_size / 2

    # Generate a regular grid for interpolation
    x = np.arange(-radius + 0.5, radius - 0.5 + step, step)
    y = np.arange(-radius + 0.5, radius - 0.5 + step, step)
    grid_x, grid_y = np.meshgrid(x, y)

    # Create a mask for points outside the valid wafer radius
    distance_from_center = np.sqrt(grid_x ** 2 + grid_y ** 2)
    mask = distance_from_center <= radius - edge_exclusion


    # Interpolate values of the threshold column onto the grid
    if threshold:
        grid_z = griddata(
            (data_frame['X'], data_frame['Y']),
            data_frame[thr_column],
            (grid_x, grid_y),
            method='linear'
        )

        # Mask invalid points and those below the threshold
        grid_z_masked = np.ma.masked_where(~mask, grid_z)
        grid_z_masked = np.ma.masked_where(grid_z_masked < threshold, grid_z_masked)

        # Save the mask as a file
        os.makedirs(os.path.join(wafer_number, "Mapping"), exist_ok=True)
        np.save(os.path.join(wafer_number, 'Mask.npy'), grid_z_masked.mask)

    i = 0  # Index to track settings and filenames
    # Process each peak and generate corresponding plots
    for column in peaks:
        # Determine color scale if identical scaling is enabled
        if identical == 'Manual':
            vmin = next((setting['Min'] for setting in settings if
                         setting['Peak'] == column), None)
            vmax = next((setting['Max'] for setting in settings if
                         setting['Peak'] == column), None)

            vmin = float(vmin) if vmin else data_frame[column].min()
            vmax = float(vmax) if vmax else data_frame[column].max()
            print(f"Manual scaling for {column}: vmin={vmin}, vmax={vmax}")

        if identical == 'Auto':
            # Locate the folder containing boxplot data.

            parent_dir = os.path.dirname(os.path.dirname(filepath))
            list_data_dir = os.path.join(parent_dir, "Liste_data")
            boxplot_file = os.path.join(list_data_dir,
                                        f"Boxplot_"
                                        f"{filenames[i].replace('_ID_scale', '')}.csv")

            if os.path.exists(boxplot_file):
                boxplot_data = pd.read_csv(boxplot_file, header=0, index_col=0)

                # Calculate vmin and vmax based on the boxplot data
                vmin = boxplot_data.min(numeric_only=True).min()
                vmax = boxplot_data.max(numeric_only=True).max()
                print(f"Auto scaling for {column}: vmin={vmin}, vmax={vmax}")
            else:
                print(
                    f"Boxplot file not found: {boxplot_file}. Using default "
                    f"scaling.")
                vmin = data_frame[column].min()
                vmax = data_frame[column].max()

        grid_z = griddata((data_frame['X'], data_frame['Y']),
                          data_frame[column],
                          (grid_x, grid_y), method='linear')

        # Apply the saved mask to the interpolated data
        if threshold:
            mask_int = np.load(os.path.join(wafer_number, 'Mask.npy'))
            grid_z = np.ma.masked_where(mask_int, grid_z)

        # Save the interpolated grid as a CSV file
        data = pd.DataFrame({
            'X': grid_x.flatten(),
            'Y': grid_y.flatten(),
            'Z': grid_z.flatten()
        })
        grid_z_pivot = data.pivot(index='Y', columns='X', values='Z')
        grid_z_pivot.to_csv(os.path.join(wafer_number,
                                         f'{grids[i]}_grid_df.csv'))

        # Create and save the plot for the current peak
        fig, ax = plt.subplots(figsize=(8, 8))
        if identical:
            img = ax.imshow(grid_z_pivot,
                            extent=(-radius, radius, -radius, radius),
                            origin='lower', cmap='Spectral_r',
                            vmin=vmin, vmax=vmax)
        else:
            img = ax.imshow(grid_z_pivot,
                            extent=(-radius, radius, -radius, radius),
                            origin='lower', cmap='Spectral_r')

        # # # Customize plot appearance
        # # ax.set_aspect('equal', adjustable='box')
        cbar = plt.colorbar(img, ax=ax, shrink=0.8)
        cbar.ax.tick_params(labelsize=28)
        ax.set_xlabel('X (mm)', fontsize=28)
        ax.set_ylabel('Y (mm)', fontsize=28)
        ax.tick_params(axis='both', labelsize=24)

        # # Add optional slot-based labeling
        if slot_number:
            ylabels[i] = f"S{os.path.basename(wafer_number)} - {ylabels[i]}"
        
        plt.title(ylabels[i], fontsize=20)

        ax.xaxis.set_major_locator(mticker.MultipleLocator(50))
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f'{int(x)}'))

        ax.yaxis.set_major_locator(mticker.MultipleLocator(50))
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda y, _: f'{int(y)}'))
        circle = plt.Circle((0, 0), radius - edge_exclusion,
                            color='black', fill=False, linewidth=1)
        ax.add_patch(circle)

        if stats:
            parent_dir = os.path.dirname(os.path.dirname(filepath))
            list_data_dir = os.path.join(parent_dir, "Liste_data")
            stats_file = os.path.join(list_data_dir, "Stats.csv")
            wafer_digit = float(os.path.basename(wafer_number))

            # Check if the Stats.csv file exists
            if os.path.exists(stats_file):
                # Load the CSV into a DataFrame
                stats_data = pd.read_csv(stats_file)

                # Filter the DataFrame to find the row corresponding to
                # wafer_number and column
                filtered_data = stats_data[
                    (stats_data['Slot'] == wafer_digit) & (
                            stats_data['Parameters'] == column)]

                if not filtered_data.empty:
                    # Extract the mean and 3sigma values
                    mean_value = filtered_data['mean'].values[0]
                    sigma_value = filtered_data['3sigma'].values[0]

                    # Add text for mean and 3sigma
                    ax.text(0.01, 0.01, f'Mean: {mean_value:.2f}',
                            transform=ax.transAxes, fontsize=14,
                            ha='left', va='bottom', color='black')
                    ax.text(0.96, 0.01, f'3$\sigma$: {sigma_value:.2f}',
                            transform=ax.transAxes, fontsize=14,
                            ha='right', va='bottom', color='black')
                else:
                    print(
                        f"No data found for wafer {wafer_digit} and column "
                        f"{column}.")
            else:
                print(f"Error: {stats_file} does not exist.")

        plt.savefig(os.path.join(wafer_number, "Mapping", f"{filenames[i]}.png"),
            bbox_inches='tight')
        plt.close(fig)
        print(f"Saved plot for {column} as {filenames[i]}.png")

        i += 1


def _apply_operation(col1, col2, operation):
    """
    Applies the specified operation between two columns.

    :param col1: First column data.
    :param col2: Second column data.
    :param operation: The mathematical operation to apply.
    :return: The resulting column.
    """
    if operation == '+':
        return col1 + col2
    if operation == '-':
        return col1 - col2
    if operation == '*':
        return col1 * col2
    if operation == '/':
        return col1 / col2


def _apply_peak_operations(data_frame, peaks_to_keep):
    """
    Applies mathematical operations on peak columns if specified.

    :param data_frame: The DataFrame to process.
    :param peaks_to_keep: List of peaks to check for operations.
    """
    for peak in peaks_to_keep:
        if any(op in peak for op in ['-', '+', '*', '/']):
            col1, col2, operation = None, None, None
            if '-' in peak:
                col1, col2 = peak.split(' - ')
                operation = '-'
            elif '+' in peak:
                col1, col2 = peak.split(' + ')
                operation = '+'
            elif '*' in peak:
                col1, col2 = peak.split(' * ')
                operation = '*'
            elif '/' in peak:
                col1, col2 = peak.split(' / ')
                operation = '/'

            if col1 in data_frame.columns and col2 in data_frame.columns:
                data_frame[peak] = _apply_operation(data_frame[col1],
                                                    data_frame[col2],
                                                    operation)


def _apply_threshold(data_frame, column, threshold):
    """
    Applies a threshold to a column and adjusts other columns accordingly.

    :param data_frame: The DataFrame to modify.
    :param column: The column to apply the threshold on.
    :param threshold: Threshold value.
    """
    mask = data_frame[column] < threshold
    data_frame.loc[mask, column] = 0
    other_columns = [col for col in data_frame.columns if
                     col not in ['X', 'Y', column]]
    data_frame.loc[mask, other_columns] = np.nan


def _adjust_x0_columns(data_frame):
    """
    Adjusts specific columns ending with 'x0'.

    :param data_frame: The DataFrame to modify.
    """
    # Stocke Si_x0 avant modification
    si_x0_ref = data_frame["Si_x0"].copy()

    for column in data_frame.columns:
        if column.endswith("x0") and not any(
                op in column for op in ['+', '-', '*', '/']):
            data_frame[column] = data_frame[column] - (si_x0_ref - 520.7)

class XRD:
    """
    Class XRF
    This class contains functions and classes for performing XRF spectra
    fitting + plotting.
    """

    def __init__(self, dirname, dirname_model, settings, input, cpu=None):
        self.dirname = dirname
        self.dirname_model = dirname_model
        self.step = 0.5
        self.cpu = cpu
        self.pbar_index = None
        self.settings_dataframe = settings
        self.input = input

        # Extract wafer properties from input
        self.wafer_size = int(self.input.get('Wafer Size', 0))
        self.edge_exclusion = int(self.input.get('Edge Exclusion', 0))
        self.radius = self.wafer_size / 2

    def progressbar(self, queue_incr, ntot, ncpus, show_progressbar):
        """ Progress bar """
        self.pbar_index = 0
        pbar = "\r[{:100}] {:.0f}% {}/{} {:.2f}s " + f"ncpus={ncpus}"
        t0 = time.time()
        while self.pbar_index < ntot:
            self.pbar_index += queue_incr.get()
            percent = 100 * self.pbar_index / ntot
            cursor = "*" * int(percent)
            exec_time = time.time() - t0
            msg = pbar.format(cursor, percent, self.pbar_index, ntot, exec_time)
            if show_progressbar:
                sys.stdout.write(msg)
        if show_progressbar:
            print()

    def decomposition(self, subdir_filter):
        """
        Decomposition function
        Decompose .txt file.
        """
        subdir_filter = [str(x).strip().lower() for x in subdir_filter]
        cpu = int(self.cpu)
        fname_json = self.dirname_model

        model_dict = load_from_json(fname_json)

        for subdir, _, files in os.walk(self.dirname):
            if os.path.basename(subdir) in subdir_filter:
                if subdir == self.dirname or os.path.basename(subdir) in \
                        {'Mapping', 'Spectra', 'Graphe', 'Liste Data'}:
                    continue
                spectra_path = os.path.join(subdir, 'Spectra')
                os.makedirs(spectra_path, exist_ok=True)

                mapping_path = os.path.join(subdir, 'Mapping')
                os.makedirs(mapping_path, exist_ok=True)

                fnames = []
                spectra = Spectra()
                for file in files:
                    fname = subdir + os.sep + file
                    if fname.endswith(".txt"):
                        spectrum = Spectrum()
                        spectrum.set_attributes(model_dict[0])
                        spectrum.fname = fname
                        fnames.append(fname)
                        spectrum.preprocess()
                        spectra.append(spectrum)

                if len(spectra) > 0:
                    queue_incr = Queue()
                    args = (queue_incr, len(fnames), cpu, True)
                    thread = Thread(target=self.progressbar, args=args)
                    thread.start()
                    fit_mp(spectra, cpu, queue_incr)
                    thread.join()
                    spectra.save_results(subdir)
                    gc.collect()
                z = 0

                # Number of peaks in model
                df_model = pd.read_json(self.dirname_model)
                peak_number = len(df_model.loc['peak_labels'][0])

                for spectrum in spectra:
                    data = {}
                    for i in range(peak_number):
                        model = spectrum.peak_models[i]
                        param_hints_orig = deepcopy(model.param_hints)
                        for key, _ in model.param_hints.items():
                            model.param_hints[key]['expr'] = ''
                        params = model.make_params()
                        model.param_hints = param_hints_orig
                        x = spectrum.x
                        y = spectrum.y
                        intensity = model.eval(params, x=x, der=0)
                        if 'x' not in data:
                            data['x'] = x
                        if 'y' not in data:
                            data['y'] = y
                        data[f'a_{i}'] = intensity
                    component = pd.DataFrame(data)
                    data_matrix_plot = \
                        os.path.splitext(os.path.basename(fnames[z]))[
                            0] + '_fitted'
                    component['sum_a'] = component[
                        [col for col in component.columns if
                         col.startswith('a_')]].sum(axis=1)
                    component = component.round(2)
                    component.to_csv(
                        subdir + os.sep + 'Spectra' + os.sep +
                        data_matrix_plot +
                        ".txt",
                        sep='\t')
                    z += 1
                del fnames, spectra

        filenames_to_remove = [".csv", "_stats.txt"]

        for subdir, _, files in os.walk(self.dirname):
            if os.path.basename(subdir) in subdir_filter:
                for file in files:

                    if file.endswith("Spectrums.csv"):
                        continue
                    if file == "results.csv":
                        continue  # Ignore 'results.csv'
                    filepath = os.path.join(subdir, file)
                    if any(name in filepath for name in filenames_to_remove):
                        os.remove(filepath)


    def decomposition_sample(self):
        """
            decomposition function
            Decompose .txt file.
        """
        cpu = int(self.cpu)
        fname_json = self.dirname_model

        model_dict = load_from_json(fname_json)

        for subdir, _, files in os.walk(self.dirname):
            if os.path.basename(subdir) in {'Spectra', 'Graphe', 'Liste Data'}:
                continue

            fnames = []
            spectra = Spectra()
            for file in files:
                fname = subdir + os.sep + file
                if fname.endswith(".txt"):
                    spectra_path = os.path.join(subdir, 'Spectra')
                    os.makedirs(spectra_path, exist_ok=True)
                    spectrum = Spectrum()
                    spectrum.set_attributes(model_dict[0])
                    spectrum.fname = fname
                    fnames.append(fname)
                    spectrum.preprocess()
                    spectra.append(spectrum)

            if len(spectra) > 0:
                queue_incr = Queue()
                args = (queue_incr, len(fnames), cpu, True)
                thread = Thread(target=self.progressbar, args=args)
                thread.start()
                fit_mp(spectra, cpu, queue_incr)
                thread.join()
                spectra.save_results(subdir)
            z = 0

            # Number of peaks in model
            df_model = pd.read_json(self.dirname_model)
            peak_number = len(df_model.loc['peak_labels'][0])
            # Number of peaks in model

            for spectrum in spectra:
                data = {}
                for i in range(peak_number):
                    model = spectrum.peak_models[i]
                    # remove temporarily 'expr' that can be related to
                    # another model
                    param_hints_orig = deepcopy(model.param_hints)
                    for key, _ in model.param_hints.items():
                        model.param_hints[key]['expr'] = ''
                    params = model.make_params()
                    model.param_hints = param_hints_orig
                    x = spectrum.x
                    y = spectrum.y
                    intensity = model.eval(params, x=x, der=0)
                    if 'x' not in data:
                        data['x'] = x
                    if 'y' not in data:
                        data['y'] = y
                    data[f'a_{i}'] = intensity
                component = pd.DataFrame(data)
                data_matrix_plot = \
                    os.path.splitext(os.path.basename(fnames[z]))[
                        0] + '_fitted'
                component['sum_a'] = component[
                    [col for col in component.columns if
                     col.startswith('a_')]].sum(axis=1)
                component = component.round(2)
                component.to_csv(
                    subdir + os.sep + 'Spectra' + os.sep +
                    data_matrix_plot +
                    ".txt",
                    sep='\t')
                z += 1
            del fnames, spectra

        filenames_to_remove = [".csv", "_stats.txt"]

        for subdir, _, files in os.walk(self.dirname):
            for file in files:
                if file == "results.csv":
                    continue  # Ignore 'results.csv'
                filepath = os.path.join(subdir, file)
                if any(name in filepath for name in filenames_to_remove):
                    os.remove(filepath)

    def create_database_sample(self):
        """
        Creates a CSV file based on the model, processing only
        specific subdirectories listed in subdir_filter.
        """

        # Load the model's JSON file and extract peak labels
        model_dict = load_from_json(self.dirname_model)
        peak_labels = model_dict[0]['peak_labels']

        # Extract peaks to retain based on the settings DataFrame
        peaks_to_keep = [setting['Peak'].strip() for setting in
                         self.settings_dataframe if setting['Peak']]

        # Initialize threshold to None
        threshold = None
        # Iterate over the settings to identify the threshold
        for i, setting in enumerate(self.settings_dataframe):
            if setting.get('Threshold'):  # Check if 'Threshold' is defined
                threshold = int(self.settings_dataframe[i]['Min'])

        # Specify the columns to retain for the output
        columns_to_keep = ['Filename'] + peaks_to_keep

        # Traverse directories under the main directory
        for subdir, _, files in os.walk(self.dirname):
            # Skip subdirectories not in the filter list
            for file in files:
                # Only process files named 'results.csv'
                if not file.startswith('results.csv'):
                    continue

                # Process the matching file
                self._process_file_sample(os.path.join(subdir, file),
                                          peak_labels,
                                          peaks_to_keep, columns_to_keep,
                                          threshold)

    def create_database(self, subdir_filter):
        """
        Creates a CSV file based on the model, processing only
        specific subdirectories listed in subdir_filter.

        :param subdir_filter: List of folder names (as strings) to process.
        """

        # Normalize and clean the subdir_filter input
        subdir_filter = [str(x).strip().lower() for x in subdir_filter]

        # Load the model's JSON file and extract peak labels
        model_dict = load_from_json(self.dirname_model)
        peak_labels = model_dict[0]['peak_labels']

        # Extract peaks to retain based on the settings DataFrame
        peaks_to_keep = [setting['Peak'].strip() for setting in
                         self.settings_dataframe if setting['Peak']]

        # Initialize threshold to None
        threshold = None
        # Iterate over the settings to identify the threshold
        for i, setting in enumerate(self.settings_dataframe):
            if setting.get('Threshold'):  # Check if 'Threshold' is defined
                threshold = int(self.settings_dataframe[i]['Min'])

        # Specify the columns to retain for the output
        columns_to_keep = ['X', 'Y'] + peaks_to_keep

        # Traverse directories under the main directory
        for subdir, _, files in os.walk(self.dirname):
            # Skip subdirectories not in the filter list
            if os.path.basename(subdir) not in subdir_filter:
                continue

            # Process files within the directory
            for file in files:
                # Only process files named 'results.csv'
                if not file.startswith('results.csv'):
                    continue

                # Process the matching file
                self._process_file(os.path.join(subdir, file), peak_labels,
                                   peaks_to_keep, columns_to_keep, threshold)

    def _process_file_sample(self, filepath, peak_labels, peaks_to_keep,
                             columns_to_keep, threshold):
        """
        Processes a single file to apply transformations and save the result.

        :param filepath: Path to the input file.
        :param peak_labels: List of peak labels from the model.
        :param peaks_to_keep: List of peaks to retain and transform.
        :param columns_to_keep: List of final columns to retain in the output.
        :param threshold: Threshold value for A1g_ampli.
        """
        data_frame = pd.read_csv(filepath, sep=';')
    

        i = 0
        # Replace peak columns (m01, m02, ...) with their labels
        for i, label in enumerate(peak_labels):
            data_frame.rename(columns=lambda col: col.replace
            (f"m0{i + 1}", label) if f"m0{i + 1}" in col else col, inplace=True)

        # Apply mathematical operations on peaks
        _apply_peak_operations(data_frame, peaks_to_keep)

        data_frame['Filename'] = data_frame['name']
        data_frame['Filename'] = data_frame['Filename'].str.replace('.txt', '')

        # Reorder columns and filter by required ones
        data_frame = data_frame[
            ['Filename'] + [col for col in data_frame if
                            col not in ['Filename']]]
        data_frame = data_frame.loc[:, data_frame.columns.isin(columns_to_keep)]

        for i, setting in enumerate(self.settings_dataframe):
            if setting.get('Threshold'):
                peak = self.settings_dataframe[i]['Peak']
                _apply_threshold(data_frame, peak, threshold)

        # Adjust specific columns ending with "x0"
        if 'Si_x0' in data_frame.columns:
            _adjust_x0_columns(data_frame)

        # Save the processed DataFrame
        output_file = os.path.join(os.path.dirname(filepath), 'data_DP.csv')
        data_frame.to_csv(output_file, index=False)

    def _process_file(self, filepath, peak_labels, peaks_to_keep,
                      columns_to_keep, threshold):
        """
        Processes a single file to apply transformations and save the result.

        :param filepath: Path to the input file.
        :param peak_labels: List of peak labels from the model.
        :param peaks_to_keep: List of peaks to retain and transform.
        :param columns_to_keep: List of final columns to retain in the output.
        :param threshold: Threshold value for A1g_ampli.
        """
        data_frame = pd.read_csv(filepath, sep=';')
        print(data_frame)

        # Replace peak columns (m01, m02, ...) with their labels
        for i, label in enumerate(peak_labels):
            if i + 1 < 10:
                pattern = f"m0{i + 1}"
            else:
                pattern = f"m{i + 1}"
            data_frame.rename(columns=lambda col: col.replace(pattern,
                                                              label) if
            pattern in col else col,
                              inplace=True)

        # Apply mathematical operations on peaks
        _apply_peak_operations(data_frame, peaks_to_keep)

        data_frame.rename(columns={'x': 'X', 'y': 'Y'}, inplace=True)

        data_frame[['X', 'Y']] = data_frame['name'].str.split('_', expand=True)
        data_frame['Y'] = data_frame['Y'].str.replace('.txt', '')
        # data_frame['X']=data_frame['x'] / 2
        # data_frame['Y']=data_frame['y'] / 2

        data_frame['X'] = pd.to_numeric(data_frame['X'], errors='coerce')
        data_frame['Y'] = pd.to_numeric(data_frame['Y'], errors='coerce')
        distance_from_center = np.sqrt(
            data_frame['X'] ** 2 + data_frame['Y'] ** 2)
        mask = distance_from_center <= (self.radius - self.edge_exclusion)

        data_frame = data_frame[mask]

        output_file = os.path.join(os.path.dirname(filepath),
                                   'data_DP_test.csv')
        data_frame.to_csv(output_file, index=False)

        # Reorder columns and filter by required ones
        data_frame = data_frame[
            ['X', 'Y'] + [col for col in data_frame if col not in ['X', 'Y']]]
        data_frame = data_frame.loc[:, data_frame.columns.isin(columns_to_keep)]


        for i, setting in enumerate(self.settings_dataframe):
            if setting.get('Threshold'):
                peak = self.settings_dataframe[i]['Peak']
                _apply_threshold(data_frame, peak, threshold)

        # Adjust specific columns ending with "x0"
        if 'Si_x0' in data_frame.columns:
            _adjust_x0_columns(data_frame)

        # Save the processed DataFrame
        output_file = os.path.join(os.path.dirname(filepath), 'data_DP.csv')
        data_frame.to_csv(output_file, index=False)

    def plot(self, slot_number=None, identical=None, wafers=None, stats=None):
        """
        Plot data using multiprocessing with automatic scaling.
        """
        filepaths = []
        if wafers is None:
            wafers = []

            # Gather all "data_DP.csv" files
        for subdir, _, files in os.walk(self.dirname):
            subdir_name = os.path.basename(subdir).strip().lower()
            wafers_str = [str(w).lower() for w in wafers]

            print(f"Comparing '{subdir_name}' with wafers {wafers_str}")
            if subdir_name in wafers_str:
                print(f"Found matching wafer: {subdir_name}")
                for file in files:
                    if file.endswith("data_DP.csv"):
                        filepaths.append(os.path.join(subdir, file))

        print(f"Found file paths: {filepaths}")

        process_partial = partial(
            plot_wdf_mp,
            settings=self.settings_dataframe,
            input=self.input,
            slot_number=slot_number,
            identical=identical,
            stats=stats,
        )

        # Determine the number of worker processes to use
        num_cpu_cores = os.cpu_count()
        max_workers = max(1, num_cpu_cores // 2)

        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            executor.map(process_partial, filepaths)




if __name__ == "__main__":
    DIRNAME = r'C:\Users\TM273821\Desktop\DRX\C24D0156'
    MODEL = r'C:\Users\TM273821\Desktop\Model\InP_XRD.json'
    SUBDIR = [1]
    # SUBDIR = [13]
    # SUBDIR = [7,9,11,13,17,19,21]

    app = QApplication(sys.argv)
    settings_window = SettingsWindow()
    settings_window.show()
    app.exec_()
    settings_table, inputs_table = settings_window.get_table_data()

    XRF = XRF(DIRNAME, MODEL, settings_table, inputs_table, cpu=4)
    # XRF.offset()
    # XRF.decomposition(SUBDIR)
    # XRF.create_database(SUBDIR)
    XRF.plot(slot_number=False, identical='Auto', wafers=SUBDIR, stats=False)
    # XRF.plot(slot_number=False, identical='Manual', wafers = SUBDIR)
    # XRF.rotate_PL()
