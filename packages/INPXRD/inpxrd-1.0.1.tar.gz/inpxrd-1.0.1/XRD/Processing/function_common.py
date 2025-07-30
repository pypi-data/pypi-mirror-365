"""
Function_common Module

This module contains functions and classes which are common to all
characterizations.
"""
import sys
import gc
import os
import shutil
from itertools import cycle, islice
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from matplotlib import rcParams
from PIL import Image
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Layout.settings import SettingsWindow
from PyQt5.QtWidgets import QApplication

import pandas as pd
import matplotlib.pyplot as plt

rcParams.update({'figure.autolayout': True})


def process_fitted_file(filepath, input):
    """
    Process a single 'fitted.txt' file and generate a spectrum plot.
    """
    print(filepath, input)
    xmin = float(input.get('Spectra xmin', 0)) if input.get(
        'Spectra xmin') else None
    xmax = float(input.get('Spectra xmax', 0)) if input.get(
        'Spectra xmax') else None
    ymin = float(input.get('Spectra ymin', 0)) if input.get(
        'Spectra ymin') else None
    ymax = float(input.get('Spectra ymax', 0)) if input.get(
        'Spectra ymax') else None

    Xlabel = input.get('Xlabel') if input.get(
        'Xlabel') else None

    Ylabel = input.get('Ylabel') if input.get(
        'Ylabel') else None


    data_frame = pd.read_csv(filepath, sep='\t', index_col=0)

    my_colors = list(islice(cycle(['k']), len(data_frame.columns[1:])))
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.tick_params(axis='both', which='major', labelsize=15)

    for i, col in enumerate(data_frame.columns[1:]):
        ax.plot(data_frame.iloc[:, 0], data_frame[col], label=col,
                color=my_colors[i])

    ax.set_xlabel(Xlabel, fontsize=20)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(Ylabel, fontsize=20)

    fitted_name = os.path.splitext(os.path.basename(filepath))[0]
    output_path = os.path.join(os.path.dirname(filepath), f"{fitted_name}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    gc.collect()


def rename_coordinates(x, y):
    """
    Updates the x and y coordinate values based on predefined mappings.

    Parameters:
    x (str): The x-coordinate to rename.
    y (str): The y-coordinate to rename.

    Returns:
    tuple: Updated x and y coordinates.
    """
    original_values = ['8.9', '-8.9', '5.9', '-5.9']
    new_values = ['9.0', '-9.0', '6.0', '-6.0']
    for i, value in enumerate(original_values):
        if x == value:
            x = new_values[i]
        if y == value:
            y = new_values[i]
    return x, y


class Common:
    """
    Common Class
    This class contains all functions.
    """

    def __init__(self, dirname, settings_var, input_var):
        self.dirname = dirname
        self.settings_dataframe = settings_var
        self.input = input_var

    def plot_spectrum(self, wafers):
        """
        Generate spectrum plots from fitted.txt files using multiprocessing.
        """
        # Create the output directory if it doesn't exist
        path = os.path.join(self.dirname, 'Graphe')
        os.makedirs(path, exist_ok=True)

        filepaths = []

        # Convert `wafers` to lowercase for consistent comparisons
        wafers_lower = [str(w).lower() for w in wafers]

        # Walk through the directory tree
        for subdir, _, files in os.walk(self.dirname):
            subdir_name = os.path.basename(subdir).strip().lower()

            # Check if the current directory matches one of the wafers
            if subdir_name in wafers_lower:
                spectra_dir = os.path.join(subdir, "Spectra")

                # Check if the "Spectra" subdirectory exists
                if os.path.exists(spectra_dir) and os.path.isdir(spectra_dir):
                    for file in os.listdir(spectra_dir):
                        # Add only files ending with "fitted.txt"
                        if file.endswith(".txt"):
                            filepaths.append(os.path.join(spectra_dir, file))
                else:
                    print(
                        f"No 'Spectra' directory in {subdir_name}")  #
                    # Debugging statement


        # Prepare partial function for multiprocessing
        process_partial = partial(process_fitted_file, input=self.input)

        # Use ProcessPoolExecutor for parallel processing
        num_cpu_cores = os.cpu_count()
        max_workers = max(1, num_cpu_cores // 2)

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            executor.map(process_partial, filepaths)

    def plot_spectrum_sample(self):
        """
        Generate spectrum plots from fitted.txt files using multiprocessing.
        """
        filepaths = []

        # Walk through the directory tree
        for subdir, _, files in os.walk(self.dirname):
            spectra_dir = os.path.join(subdir, "Spectra")

            # Check if the "Spectra" subdirectory exists
            if os.path.exists(spectra_dir) and os.path.isdir(spectra_dir):
                for file in os.listdir(spectra_dir):
                    # Add only files ending with "fitted.txt"
                    if file.endswith(".txt"):
                        filepaths.append(os.path.join(spectra_dir, file))
                else:
                    print(
                        f"No 'Spectra' directory")  #
                    # Debugging statement

        # Print collected file paths for verification
        print(f"Filtered file paths: {filepaths}")

        # Prepare partial function for multiprocessing
        process_partial = partial(process_fitted_file, input=self.input)

        # Use ProcessPoolExecutor for parallel processing
        num_cpu_cores = os.cpu_count()
        max_workers = max(1, num_cpu_cores // 2)

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            executor.map(process_partial, filepaths)

    def create_image_grid(self, zscale=None):
        """
        Plots an image grid based on selected zscale and material type.
        """
        # Extraire filename from settings
        filenames = [setting['Filename'].strip() for setting in
                     self.settings_dataframe if setting['Filename']]

        image_options = {
            'Auto': [filename + '.png' for filename in filenames],
            'Identical': [filename + '_ID_scale.png' for filename in filenames],
        }

        image_names = image_options.get(zscale)

        # Get sorted subfolders
        def sort_key(subfolder_name):
            parts = subfolder_name.split("\\")
            for part in parts:
                if part.isdigit():
                    return int(part)
            return float('inf')

        subfolders = sorted(
            [f.path for f in os.scandir(self.dirname) if f.is_dir()],
            key=sort_key)

        # Calculate grid dimensions
        num_subfolders = len(subfolders)
        rows = -(-num_subfolders // 5)  # Ceiling division

        # Load images from subfolders
        images_list = []
        for image_name in image_names:
            sub_images = [Image.open(os.path.join(subfolder,
                                                  "Mapping", image_name))
                          for subfolder in subfolders if
                          os.path.exists(os.path.join(subfolder,
                                                      "Mapping", image_name))]
            images_list.append(sub_images)

        # Determine grid dimensions based on image sizes
        image_spacing = 50
        grid_width, grid_height = 0, 0
        for sub_images in images_list:
            for image in sub_images:
                grid_width = max(grid_width, 5 * image.width)
                grid_height = max(grid_height, rows * image.height)

        # Create blank grid images and paste images into the grid
        grid_images = [Image.new('RGB', (grid_width + 250, grid_height + 200),
                                 (255, 255, 255))
                       for _ in image_names]

        for idx, sub_images in enumerate(images_list):
            for i, image in enumerate(sub_images):
                x, y = (i % 5) * (image.width + image_spacing), (i // 5) * (
                        image.height + image_spacing)
                grid_images[idx].paste(image, (x, y))

        # Save merged grid images
        save_path = os.path.join(self.dirname, "Graphe", "Mapping")
        os.makedirs(save_path, exist_ok=True)
        for idx, grid_image in enumerate(grid_images):
            grid_image.save(os.path.join(save_path, f"All_{image_names[idx]}"))

    def reboot(self, subdir_filter, split=False):
        """
        Delete unnecessary files.
        """
        subdir_filter = [str(x).strip().lower() for x in subdir_filter]

        for subdir, _, files in os.walk(self.dirname):
            subdir_name = os.path.basename(subdir).strip().lower()
            print(f"Sub directory : {subdir_name}")
            if subdir_name in subdir_filter:
                for folder in ["Graphe", "Mapping", "Spectra", "raw_data",
                               "Liste_data"]:
                    path = os.path.join(self.dirname, folder)
                    path_2 = os.path.join(subdir, folder)

                    if os.path.exists(path):
                        shutil.rmtree(path)
                        print(f"Deleted: {path}")

                    if os.path.exists(path_2):
                        shutil.rmtree(path_2)
                        print(f"Deleted: {path_2}")

        if split:
            filenames_to_remove = {".csv", ".png", ".txt", ".npy",
                                   "mapping.txt",
                                   "Parameters.txt", "Parameters_stats", ".wdf",
                                   "fitted", "_stats"}
        else:
            filenames_to_remove = {".csv", ".png", ".npy",
                                   "mapping.txt",
                                   "Parameters.txt", "Parameters_stats", ".wdf",
                                   "fitted", "_stats"}

        for subdir, dirs, files in os.walk(self.dirname):
            subdir_name = os.path.basename(subdir).strip().lower()
            if subdir_name in subdir_filter:
                for file in files:
                    filepath = os.path.join(subdir, file)

                    # Skip files ending with "Spectrums.csv"
                    if file.endswith("Spectra.csv") or file.endswith("Spectrums.csv"):
                        print(f"Skipping file: {filepath}")
                        continue

                    # Check for other files to remove
                    if any(file.endswith(extension) or extension in file for
                           extension in filenames_to_remove):
                        try:
                            os.remove(filepath)
                            print(f"Deleted file: {filepath}")
                        except FileNotFoundError:
                            print(
                                f"File not found (already deleted?): "
                                f"{filepath}")
                        except Exception as err:
                            print(
                                f"Error while deleting file {filepath}: {err}")

    def reboot_sample(self):
        """
        Delete unnecessary files.
        """

        filenames_to_remove = {".csv", ".png", ".npy",
                               "mapping.txt",
                               "Parameters.txt", "Parameters_stats", ".wdf",
                               "fitted", "_stats"}

        for subdir, dirs, files in os.walk(self.dirname):
            for file in files:
                filepath = os.path.join(subdir, file)
                if any(file.endswith(extension) or extension in file for
                       extension in filenames_to_remove):
                    try:
                        os.remove(filepath)
                        print(f"Deleted file: {filepath}")
                    except FileNotFoundError:
                        print(
                            f"File not found (already deleted?): "
                            f"{filepath}")
                    except Exception as err:
                        print(
                            f"Error while deleting file {filepath}: {err}")

    def plot_columns(self):
        """
        Creates a plot for each column (ordinate) using the first column as
        the x-axis.

        This function iterates through subdirectories to find
        "data_DP.csv" files,
        extracts the data, and generates scatter plots for each column except
        the first one.

        """

        figure_height = 12
        figure_width = 8
        xtick_rotation = 45

        # Map peaks to Y-axis labels and filenames
        peak_to_label_filename = {
            setting["Peak"]: (setting["Ylabel"], setting["Filename"])
            for setting in self.settings_dataframe
        }

        # Iterate through subdirectories to find "data_DP.csv" files
        for subdir, _, files in os.walk(self.dirname):
            for file in files:
                if file.endswith("data_DP.csv"):
                    graph_path = os.path.join(subdir, "Graphe")
                    os.makedirs(graph_path, exist_ok=True)
                    filepath = os.path.join(subdir, file)
                    data = pd.read_csv(filepath)

                    # Identify the first column as the x-axis
                    x_col = data.columns[0]

                    filtered_data = data.dropna(
                        subset=[x_col] + list(data.columns[1:]))
                    x_values = filtered_data[x_col].astype(str)

                    for col in filtered_data.columns[1:]:
                        if col not in peak_to_label_filename:
                            print(
                                f"Warning: No parameter found for column "
                                f"{col}. Skipping.")
                            continue

                        ylabel, filename = peak_to_label_filename[col]

                        # Create a plot for the column
                        fig, ax = plt.subplots(
                            figsize=(figure_height, figure_width))
                        ax.scatter(x_values, filtered_data[col], marker='s',
                                   color='b', s=50)
                        ax.tick_params(axis='both', which='major', labelsize=15)
                        ax.set_ylabel(ylabel, fontsize=26)
                        plt.xticks(rotation=xtick_rotation)

                        # Save the plot
                        plot_filepath = os.path.join(graph_path,
                                                     f"{filename}.png")
                        plt.savefig(plot_filepath, bbox_inches='tight')
                        plt.close()

    def plot_boxplot(self):
        """
        Create and save a boxplot for each peak based on the data in the CSV
        files.
        The plot is saved in a specific directory and the corresponding data
        is also saved in CSV format.
        """
        # Define paths for saving output files
        path_liste = os.path.join(self.dirname, 'Liste_data')
        if not os.path.exists(path_liste):
            os.makedirs(path_liste)

        figure_height = 12
        figure_width = 8

        path2 = os.path.join(self.dirname, "Graphe", "Boxplot")
        if not os.path.exists(path2):
            os.makedirs(path2)

        taille_df = []
        peaks = [setting['Peak'].strip() for setting in self.settings_dataframe
                 if setting['Ylabel']]

        # Map peaks to their corresponding Ylabels and filenames
        peak_to_label_filename = {
            setting["Peak"]: (setting["Ylabel"], setting["Filename"])
            for setting in self.settings_dataframe
        }

        # Iterate through files and find a valid "data_DP.csv"
        for subdir, _, files in os.walk(self.dirname):
            for file in files:
                filepath = os.path.join(subdir, file)
                if filepath.endswith("data_DP.csv"):
                    data_frame = pd.read_csv(filepath)

                    if data_frame is not None and not data_frame.empty:
                        taille_df = data_frame.shape
                        if len(taille_df) >= 2:
                            # If the dataframe has at least 2 dimensions,
                            # determine column count
                            column_number = taille_df[1] - 2
                        else:
                            print("Error: DataFrame has an invalid format.")
                            return
                    else:
                        print(f"The file {filepath} is empty or invalid.")
                        return

        if not taille_df:
            print("Error: No valid file was found.")
            return

        # Proceed to process peaks
        column_number = taille_df[1] - 2

        for peak in peaks:
            ylabel, filename = peak_to_label_filename[peak]
            col_data = {}

            # Iterate through subdirectories to collect data for each peak
            for subdir, _, files in os.walk(self.dirname):
                for file in files:
                    filepath = os.path.join(subdir, file)
                    if filepath.endswith("data_DP.csv"):
                        data_frame = pd.read_csv(filepath)
                        data_frame.columns = data_frame.columns.str.strip()
                        if not data_frame.empty:
                            # Use subdirectory name as the column name
                            nom_colonne = os.path.basename(subdir)
                            col_data[nom_colonne] = data_frame.loc[:, peak]

            # Create a DataFrame from the collected data
            df_merged = pd.DataFrame(col_data)
            df_merged = df_merged[~np.isnan(df_merged)]  # Remove NaN values

            # Reset index of DataFrame
            df_merged.reset_index(drop=True, inplace=True)

            # Ensure column names are integers for sorting
            df_merged.columns = df_merged.columns.astype(int)

            # Sort columns by index
            df_merged = df_merged.sort_index(axis=1)

            # Replace 0 values with NaN
            df_merged[df_merged == 0] = np.nan

            # Prepare data for the boxplot (removing NaN values)
            data_for_boxplot = [df_merged[col].dropna().values for col in
                                df_merged.columns]

            # Re-create the DataFrame with cleaned data for the boxplot
            df_merged = pd.DataFrame({
                col: pd.Series(data)
                for col, data in zip(df_merged.columns, data_for_boxplot)
            })

            # Save the cleaned data to a CSV file
            nouveau_fichier = f"Boxplot_{filename}.csv"
            df_merged.to_csv(os.path.join(path_liste, nouveau_fichier))

            # Plot the boxplot
            fig, ax = plt.subplots(figsize=(figure_height, figure_width))
            ax.tick_params(axis='both', which='major', labelsize=15)
            ax.boxplot([df_merged[col].dropna() for col in df_merged.columns],
                       showfliers=False)
            ax.set_xticklabels(df_merged.columns)
            ax.set_xlabel('Wafer', fontsize=26)
            ax.set_ylabel(ylabel, fontsize=26)

            # Save the plot as a PNG image
            plot_filepath = os.path.join(path2, f"{filename}.png")
            plt.savefig(plot_filepath, bbox_inches='tight')
            plt.close()

    def stats(self):
        """
            stats function
            Create Parameters files. Calculate the mean value for each
            .
        """

        path_liste = os.path.join(self.dirname, 'Liste_data')
        if not os.path.exists(path_liste):
            os.makedirs(path_liste)

        filename = "data_DP.csv"
        filename_parameters = 'Parameters.csv'
        for subdir, _, files in os.walk(self.dirname):
            for file in files:
                filepat = subdir + os.sep
                filepath = subdir + os.sep + file
                if filepath.endswith(filename):
                    os.chdir(filepat)
                    data_frame = pd.read_csv(filepath)
                    stat = data_frame.describe()
                    mod_dataframe = stat.drop(
                        ['count', '25%', '50%', '75%'])
                    mod_dataframe.iloc[1, :] = mod_dataframe.iloc[1, :] * 3
                    mod_dataframe = mod_dataframe.rename(
                        index={'std': '3sigma'})
                    mod_dataframe = mod_dataframe.transpose()

                    mod_dataframe.to_csv(filename_parameters)
                    mod_dataframe = mod_dataframe.drop(
                        ['X', 'Y'])

                    slot_number = \
                        os.path.split(os.path.dirname(filepath))[
                            -1]
                    mod_dataframe['Slot'] = slot_number
                    mod_dataframe.to_csv(filename_parameters)

        parameters_dataframe = pd.DataFrame(
            columns=['Unnamed: 0', 'mean', '3sigma', 'min', 'max'])
        for subdir, dirs, files in os.walk(self.dirname):
            for file in files:
                filepat = subdir + os.sep
                filepath = subdir + os.sep + file
                if filepath.endswith(filename_parameters):
                    os.chdir(filepat)
                    data_frame = pd.read_csv(filepath)
                    parameters_dataframe = pd.concat(
                        [parameters_dataframe, data_frame])

        # Reorder columns to have 'Slot' as the first column
        cols = ['Slot'] + [col for col in
                           parameters_dataframe.columns if
                           col != 'Slot']
        parameters_dataframe = parameters_dataframe[cols]

        parameters_dataframe = parameters_dataframe.rename(
            columns={'Unnamed: 0': 'Parameters'})
        parameters_dataframe.to_csv(
            self.dirname + os.sep + "Liste_data" + os.sep + 'Stats.csv',
            index=False)

    

   
        """
        Renames files based on their x and y coordinates and applies a
        subdirectory filter.
        """
        for root, _, files in os.walk(self.dirname):
            if os.path.basename(root) == 'Spectra':
                for file in files:
                    if file.endswith(".png"):
                        parts = file.split('_')
                        x = parts[0]
                        y = parts[1]
                        x, y = rename_coordinates(x, y)
                        new_name = f'{x}_{y}_fitted.png'
                        new_path = os.path.join(root, new_name)

                        # Check if the target filename already exists
                        if os.path.exists(new_path):
                            print(
                                f"File already exists: {new_path}, skipping "
                                f"rename.")
                            continue

                        # Rename the file
                        os.rename(os.path.join(root, file), new_path)
                        print(f'{os.path.join(root, file)} -> {new_path}')

    def process_xo1_files(self):
        """
        Process .X01 files in a parent directory and its subdirectories:
        - Remove everything before line 67
        - Rename files to .txt
        
        Args:
            parent_directory (str): Path to the parent directory containing subdirectories
                                with .X01 files to process
        
        Example:
            Expected structure:
            parent_directory/
            ├── wafer1/
            │   ├── file1.X01
            │   └── file2.X01
            ├── wafer2/
            │   └── file3.X01
            └── wafer3/
                └── file4.X01
        """
        xo1_files = []
        
        # Utiliser os.walk pour parcourir le dossier parent et ses sous-répertoires
        for root, dirs, files in os.walk(self.dirname):
            for file in files:
                if file.endswith('.X01'):
                    xo1_files.append(os.path.join(root, file))
        
        if not xo1_files:
            print("No .X01 files found in the parent directory and its subdirectories.")
            return
        
        print(f"Found {len(xo1_files)} .X01 file(s) to process:")
        for file in xo1_files:
            print(f"  - {file}")
        
        print("\nProcessing in progress...")
        
        for xo1_file in xo1_files:
            try:
                # Lire le contenu du fichier
                with open(xo1_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Check if the file has at least 67 lines
                if len(lines) < 67:
                    print(f"  ⚠️  {xo1_file}: File has less than 67 lines ({len(lines)} lines)")
                    continue
                
                # Keep only lines from line 67 onwards (index 66)
                content_from_line_67 = lines[66:]
                
                # Create the new filename (.txt)
                txt_file = xo1_file.replace('.X01', '.txt')
                
                # Write the new content to the .txt file
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.writelines(content_from_line_67)
                
                # Remove the old .X01 file
                os.remove(xo1_file)
                
                print(f"  ✅ {xo1_file} → {txt_file} (removed {len(lines) - len(content_from_line_67)} lines)")
                
            except Exception as e:
                print(f"  ❌ Error processing {xo1_file}: {str(e)}")
        
        print("\nProcessing completed!")

    def rename_txt_files(self):
        """
        Process .txt files in a parent directory and its subdirectories:
        - Extract X and Y components from filename (split by "_")
        - Rename files to X_Y.txt
        
        Args:
            parent_directory (str): Path to the parent directory containing subdirectories
                                with .txt files to process
        
        Example:
            Expected structure:
            parent_directory/
            ├── wafer1/
            │   ├── file1_X_Y.txt
            │   └── file2_X_Y.txt
            ├── wafer2/
            │   └── file3_X_Y.txt
            └── wafer3/
                └── file4_X_Y.txt
        """
        txt_files = []
        
        # Utiliser os.walk pour parcourir le dossier parent et ses sous-répertoires
        for root, dirs, files in os.walk(self.dirname):
            for file in files:
                if file.endswith('.txt'):
                    # Vérifier si le fichier correspond au pattern X01 (contient au moins 2 "_")
                    name_without_ext = os.path.splitext(file)[0]
                    if len(name_without_ext.split("_")) >= 3:
                        txt_files.append(os.path.join(root, file))
        
        if not txt_files:
            print("No .txt files found in the parent directory and its subdirectories.")
            return
        
        print(f"Found {len(txt_files)} .txt file(s) to rename:")
        for file in txt_files:
            print(f"  - {file}")
        
        print("\nRenaming in progress...")
        
        for txt_file in txt_files:
            try:
                # Obtenir le nom de fichier sans le chemin
                filename = os.path.basename(txt_file)
                # Obtenir le nom sans l'extension
                name_without_ext = os.path.splitext(filename)[0]
                
                # Split par "_"
                parts = name_without_ext.split("_")
                
                if len(parts) < 4:
                    print(f"  ℹ️  {txt_file}: File already renamed, skipped")
                    continue
                            
                # Take the second and third components (index 1 and 2)
                x_component = str(round(float(parts[1]), 1))
                y_component = str(round(float(parts[2]), 1))
                
                # Create the new filename
                new_filename = f"{x_component}_{y_component}.txt"
                new_filepath = os.path.join(os.path.dirname(txt_file), new_filename)
                
                # Check if the new file already exists
                if os.path.exists(new_filepath) and new_filepath != txt_file:
                    print(f"  ⚠️  {txt_file}: File {new_filename} already exists, adding suffix")
                    counter = 1
                    while os.path.exists(new_filepath):
                        new_filename = f"{x_component}_{y_component}_{counter}.txt"
                        new_filepath = os.path.join(os.path.dirname(txt_file), new_filename)
                        counter += 1
                
                # Rename the file
                os.rename(txt_file, new_filepath)
                
                print(f"  ✅ {filename} → {new_filename}")
                
            except Exception as e:
                print(f"  ❌ Error renaming {txt_file}: {str(e)}")
        
        print("\nRenaming completed!")

if __name__ == "__main__":
    DIRNAME = r'C:\Users\TM273821\Desktop\DRX\C24D0156 - Copie'
    MODEL = r'C:\Users\TM273821\Desktop\Model\MoS2.json'
    # SUBDIR = [2,4,6,8,10,12,14,16,18,20]
    SUBDIR = [1]
    # SUBDIR = [7,9,11,13,17,19,21]

    app = QApplication(sys.argv)
    settings_window = SettingsWindow()
    settings_table, input_table = settings_window.get_table_data()
    settings_window.show()
    app.exec_()

    Common = Common(DIRNAME, settings_table, input_table)
    # Common.reboot(SUBDIR)
    # Common.spectra_split(SUBDIR, si_calib=True)
    # Common.rename()
    # Common.plot_columns()
    # Common.stats()
    # Common.plot_boxplot()
    Common.plot_spectrum(SUBDIR)


    # Common.create_image_grid(zscale="Identical")
    # Common.create_image_grid(zscale="Identical")
