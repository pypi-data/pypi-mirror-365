"""Module for managing buttons in the interface."""
import os
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QGroupBox, QGridLayout, QFileDialog, QButtonGroup, QProgressDialog, QRadioButton,QCheckBox, QSizePolicy)
from PyQt5.QtGui import QFont  # Import QFont to change font size
from PyQt5.QtCore import Qt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Layout.settings import SettingsWindow
from Processing.function_common import Common
from Processing.xrd import XRD
from Layout.style import common_radiobutton_style, function_radiobutton_style, toggle_button_style, checkbox_style, run_button_style, settings_button_style, checkbox_style_num_slot, group_box_style, get_checkbox_style_valid, get_checkbox_style_invalid
from Layout.utils_button import create_fitspy_button

class ButtonFrame(QWidget):
    """Class to create the various buttons of the interface"""

    def __init__(self, layout):
        super().__init__()
        self.layout = layout
        self.folder_path = None
        self.check_vars = {}
        self.wdXRD_class = None
        self.common_class = None
        self.entries = {}
        self.user_folder = os.path.expanduser("~")
        self.new_folder = os.path.join(self.user_folder, "Raman")



        self.create_directory(self.new_folder)
        self.data_file = os.path.join(self.new_folder, "previous_model.json")
        

        self.dirname = None
        self.recipe = None
        self.load_recipe()

        if not os.path.exists(self.new_folder):
            os.makedirs(self.new_folder)

        tool_radiobuttons_wafer = ["Fitting", "Clean", "Create Database/Boxplot", "Rename"]
        
        tool_radiobuttons_sample = ["Fitting", "Clean"]

        # Création d’un seul groupe de boutons exclusifs
        self.exclusive_group = QButtonGroup()
        self.exclusive_group.setExclusive(True)


        checkboxes = [
            ("Data processing", True), ("Autoscale mapping", True),
            ("Id. scale mapping", False), ("Id. scale mapping (auto)", True),
            ("Slot number", True), ("Stats", True)
        ]

        self.radio_buttons_wafer = {text: QRadioButton(text) for text in
                              tool_radiobuttons_wafer}
        self.radio_buttons_sample = {text: QRadioButton(text) for text in
                              tool_radiobuttons_sample}
        self.check_boxes = {text: QCheckBox(text) for text, state in checkboxes}

        self.auto = QRadioButton("Auto")
        self.auto.setChecked(True)
        self.identical_manual = QRadioButton("Identical Manual")
        self.identical_auto = QRadioButton("Identical Auto")

        for text, checkbox in self.check_boxes.items():
            checkbox.setChecked(
                checkboxes[[c[0] for c in checkboxes].index(text)][1])

        for radiobuttons in self.radio_buttons_wafer.values():
            radiobuttons.setStyleSheet(function_radiobutton_style())
        
        for radiobuttons in self.radio_buttons_sample.values():
            radiobuttons.setStyleSheet(function_radiobutton_style())

        for checkboxes in self.check_boxes.values():
            checkboxes.setStyleSheet(checkbox_style())

        self.check_boxes["Slot number"].setStyleSheet(checkbox_style_num_slot())
        self.check_boxes["Stats"].setStyleSheet(checkbox_style_num_slot())

        for btn in self.radio_buttons_wafer.values():
            self.exclusive_group.addButton(btn)

        for btn in self.radio_buttons_sample.values():
            self.exclusive_group.addButton(btn)


        max_characters = 20
        if self.dirname:
            self.display_text = self.dirname if len(
                self.dirname) <= max_characters else self.dirname[
                                                     :max_characters] + '...'

        if self.recipe:
            self.display_recipe_text = self.recipe if len(
                self.recipe) <= max_characters else self.recipe[
                                                     :max_characters] + '...'

        # Add widgets to the grid layout provided by the main window
        self.settings_window = SettingsWindow()

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        # Add widgets to the grid layout provided by the main window

        self.settings_window = SettingsWindow()
        self.dir_box()
        self.recipe_box()
        self.create_functions()
        self.create_sample_functions()
        self.create_wafer()
        self.create_run_button()
        self.selected_function_button()
        self.add_settings_button()
        self.image_radiobuttons()
        self.create_scale_box()
        create_fitspy_button(self.layout)
        self.settings_window.data_updated.connect(self.refresh_radiobuttons)

    def save_recipe(self):
        """Save the current recipe to a JSON file."""
        if self.recipe:
            try:
                with open(self.data_file, "w") as file:
                    json.dump({"recipe": self.recipe}, file)
                print("Recipe saved successfully.")
            except Exception as e:
                print(f"Failed to save recipe: {e}")

    def load_recipe(self):
        """Load the recipe from a JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as file:
                    data = json.load(file)
                    self.recipe = data.get("recipe", None)
                    print(f"Loaded recipe: {self.recipe}")
            except Exception as e:
                print(f"Failed to load recipe: {e}")

    def refresh_radiobuttons(self):
        """Recreates the radio buttons after a data update in the Settings."""
        self.image_radiobuttons()

    def create_directory(self, path):
        """Create the directory if it does not exist."""
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory created: {path}")
        else:
            print(f"Directory already exists: {path}")

    def add_settings_button(self):
        """Add a Settings button that opens a new dialog"""
        settings_button = QPushButton("Settings")
        settings_button.setStyleSheet(settings_button_style())
        settings_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        settings_button.clicked.connect(self.open_settings_window)
        self.layout.addWidget(settings_button, 0, 5, 1, 1)

    def open_settings_window(self):
        """Open the settings window"""

        self.settings_window.exec_()

    def dir_box(self):
        """Create a smaller directory selection box"""

        # Create layout for this frame
        frame_dir = QGroupBox("Directory")

        frame_dir.setStyleSheet(group_box_style())

        # Button for selecting folder
        select_folder_button = QPushButton("Select Parent Folder...")

        select_folder_button.setStyleSheet(settings_button_style())

        # Create layout for the frame and reduce its margins
        frame_dir_layout = QGridLayout()
        frame_dir_layout.setContentsMargins(10, 30, 10, 10)
        frame_dir.setLayout(frame_dir_layout)

        # Label for folder path
        if self.dirname:
            self.folder_path_label = QLabel(self.display_text)
        else:
            self.folder_path_label = QLabel()

        self.folder_path_label.setStyleSheet("""
            font-size: 12px;           /* Smaller font size */
            border: none;
        """)

        # Connect the button to folder selection method
        select_folder_button.clicked.connect(self.on_select_folder_and_update)

        # Add widgets to layout
        frame_dir_layout.addWidget(select_folder_button, 1, 0)
        frame_dir_layout.addWidget(self.folder_path_label, 2, 0)

        # Add frame to the main layout with a smaller footprint
        self.layout.addWidget(frame_dir, 0, 0, 1, 1)

    def recipe_box(self):
        """Create a smaller directory selection box"""

        # Create layout for this frame
        frame_dir = QGroupBox("Model")

        frame_dir.setStyleSheet(group_box_style())

        # Button for selecting folder
        select_folder_button = QPushButton("Select a model...")
        select_folder_button.setStyleSheet(settings_button_style())

        # Create layout for the frame and reduce its margins
        frame_dir_layout = QGridLayout()
        frame_dir_layout.setContentsMargins(10, 20, 10, 10)  # Reduced margins
        frame_dir.setLayout(frame_dir_layout)

        # Label for folder path
        if self.recipe:
            self.recipe_path_label = QLabel(self.display_recipe_text)
        else:
            self.recipe_path_label = QLabel("Recipe?")

        self.recipe_path_label.setStyleSheet("""
            font-size: 12px;           /* Smaller font size */
            border: none;
        """)

        # Connect the button to folder selection method
        select_folder_button.clicked.connect(self.on_select_recipe)

        # Add widgets to layout
        frame_dir_layout.addWidget(select_folder_button, 0, 1, 1, 1)
        frame_dir_layout.addWidget(self.recipe_path_label, 1, 1, 1, 1)

        # Add frame to the main layout with a smaller footprint
        self.layout.addWidget(frame_dir, 1, 0)

    def folder_var_changed(self):
        """Update parent folder"""
        return self.dirname

    def on_select_folder_and_update(self):
        """Method to select folder and update checkbuttons"""
        self.select_folder()
        self.update_wafers()

    def on_select_recipe(self):
        """Method to select folder and update checkbuttons"""
        self.select_recipe()

    def update_wafers(self):
        """Update the appearance of checkboxes based on the existing
        subdirectories in the specified directory."""
        if self.dirname:
            # List the subdirectories in the specified directory
            subdirs = [d for d in os.listdir(self.dirname) if
                       os.path.isdir(os.path.join(self.dirname, d))]

            # Update the style of checkboxes based on the subdirectory presence
            for number in range(1, 27):
                checkbox = self.check_vars.get(number)
                if checkbox:
                    if str(number) in subdirs:
                        checkbox.setStyleSheet(get_checkbox_style_valid())
                    else:
                        checkbox.setStyleSheet(get_checkbox_style_invalid())
        else:
            # Default style for all checkboxes if no directory is specified
            for number in range(1, 27):
                checkbox = self.check_vars.get(number)
                checkbox.setStyleSheet(get_checkbox_style_invalid())

    def image_radiobuttons(self):
        """Create a grid of radio buttons for wafer slots with exclusive selection."""
        self.table_data, input =self.settings_window.get_table_data()
        print(self.table_data)
        N = len(self.table_data)
        print(N)

        group_box = QGroupBox("Fit param.")  # Add a title to the group
        group_box.setStyleSheet(group_box_style())

        wafer_layout = QGridLayout()
        wafer_layout.setContentsMargins(10, 20, 10, 10)
        wafer_layout.setSpacing(5)  # Reduce spacing between widgets

        self.table_vars = {}  # Store references to radio buttons

        # Add radio buttons from 1 to 24, with 12 radio buttons per row
        for i in range(N):
            Label = str(self.table_data[i]["Filename"])
            radio_button = QRadioButton(Label)
            radio_button.setStyleSheet(common_radiobutton_style())

            # Connect the radio button to a handler for exclusive selection
            radio_button.toggled.connect(self.get_selected_image)
            self.table_vars[i] = radio_button

            # Calculate the row and column for each radio button in the layout
            row = (i) // 3  # Row starts at 1 after the label
            col = (i) % 3  # Column ranges from 0 to 11

            wafer_layout.addWidget(radio_button, row, col)

        group_box.setLayout(wafer_layout)

        # Add the QGroupBox to the main layout
        self.layout.addWidget(group_box, 2, 4, 1, 1)

    def create_scale_box(self):
        """Create labels and entries for Wafer values and mapping settings."""

        # Create a new QGroupBox for mapping settings
        mapping_frame = QGroupBox("Scale settings")
        mapping_frame.setStyleSheet(group_box_style())

        # Create a layout for the group box
        mapping_layout = QGridLayout()
        mapping_frame.setLayout(mapping_layout)

        scalebuttons = [self.auto, self.identical_manual, self.identical_auto]

        # Apply styling to the radio buttons
        for radiobutton in scalebuttons:
            radiobutton.setStyleSheet(common_radiobutton_style())

        # Add radio buttons to the layout
        mapping_layout.addWidget(self.auto, 0, 0)
        mapping_layout.addWidget(self.identical_manual, 0, 1)
        mapping_layout.addWidget(self.identical_auto, 0, 2)

        # Add the mapping frame to the main layout (ensure `self.layout` exists and is a QGridLayout)
        if hasattr(self, 'layout') and isinstance(self.layout, QGridLayout):
            self.layout.addWidget(mapping_frame, 3, 4, 1, 1)
        else:
            raise AttributeError(
                "The 'self.layout' attribute must be a QGridLayout instance.")

        # Reduce layout margins and spacing
        mapping_layout.setContentsMargins(5, 15, 5, 5)
        mapping_layout.setSpacing(5)  # Adjusted spacing for a balanced look

    def get_values(self):
        """Return the values from the input fields and
        radio buttons as a dictionary."""
        values = {}

        # Add the selected radio button value
        if self.auto.isChecked():
            values["Scale Type"] = "Autoscale"
        elif self.identical_manual.isChecked():
            values["Scale Type"] = "Identical scale"
        elif self.identical_auto.isChecked():
            values["Scale Type"] = "Identical scale auto"

        return values

    def get_selected_image(self):
        """Track the selected radio button."""
        selected_number = None  # Variable to store the selected radio button number
        Ntypes= len(self.table_vars.items())
        # Iterate over all radio buttons
        for number, radio_button in self.table_vars.items():

            if radio_button.isChecked():
                selected_number = number  # Track the currently selected radio button

        if selected_number is not None:
            print(f"Radio Button {selected_number} is selected.")
            self.selected_image = selected_number  # Store the selected option for further use
            return self.selected_image, Ntypes

    def get_wafer_states(self):
        """
        Récupère les listes des checkboxes basées sur les subdirectories présents
        et celles qui sont cochées.

        Returns:
            tuple: (checkboxes_with_subdirs, checked_checkboxes)
                - checkboxes_with_subdirs (list): Liste des checkboxes avec des subdirectories correspondants.
                - checked_checkboxes (list): Liste des checkboxes qui sont cochées.
        """
        checkboxes_with_subdirs = []
        checked_checkboxes = []

        if self.dirname:
            # Liste des sous-dossiers dans le répertoire spécifié
            subdirs = {str(d) for d in os.listdir(self.dirname) if
                       os.path.isdir(os.path.join(self.dirname, d))}

            # Parcourir toutes les checkboxes et vérifier les conditions
            for number, checkbox in self.check_vars.items():
                if str(number) in subdirs:
                    checkboxes_with_subdirs.append(number)
                if checkbox.isChecked():
                    checked_checkboxes.append(number)
        else:
            # Si aucun répertoire n'est spécifié, vérifier seulement les checkboxes cochées
            for number, checkbox in self.check_vars.items():
                if checkbox.isChecked():
                    checked_checkboxes.append(number)

        return checkboxes_with_subdirs, checked_checkboxes

    def create_functions(self):
        """Create radio buttons for tools and a settings button."""

        # Create a QGroupBox for "Functions (Wafer)"
        frame = QGroupBox("Functions (Wafer)")
        frame.setStyleSheet(group_box_style())
        frame_layout = QGridLayout(frame)

        # Add radio buttons to the frame layout
        frame_layout.addWidget(self.radio_buttons_wafer["Fitting"], 0, 0)
        frame_layout.addWidget(self.radio_buttons_wafer["Clean"], 1, 0)
        frame_layout.addWidget(self.radio_buttons_wafer["Create Database/Boxplot"], 2, 0)
        frame_layout.addWidget(self.radio_buttons_wafer["Rename"], 3, 0)

        # Add the frame to the main layout
        self.layout.addWidget(frame, 0, 1, 2, 2)  # Add frame to main layout

    def create_sample_functions(self):
        """Create radio buttons for tools and a settings button."""

        frame = QGroupBox("Functions (Samples)")
        frame.setStyleSheet(group_box_style())

        frame_layout = QGridLayout(frame)

        # Add radio buttons to the frame layout
        frame_layout.addWidget(self.radio_buttons_sample["Fitting"], 0, 0)
        frame_layout.addWidget(self.radio_buttons_sample["Clean"], 1, 0)

        # Add the frame to the main layout
        self.layout.addWidget(frame, 0, 3, 2, 1)  # Add frame to main layout

    

    def create_wafer(self):
        """Create a grid of checkboxes for wafer slots with a toggle button."""
        group_box = QGroupBox("Wafer Slots")  # Add a title to the group
        group_box.setStyleSheet(group_box_style())

        wafer_layout = QGridLayout()
        wafer_layout.setContentsMargins(2, 5, 2, 2)  # Reduce internal margins
        wafer_layout.setSpacing(5)  # Reduce spacing between widgets

        # Create a button to toggle all checkboxes
        toggle_button = QPushButton("Select/Deselect All")
        toggle_button.setStyleSheet(toggle_button_style())
        toggle_button.clicked.connect(self.toggle_checkboxes)
        toggle_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        wafer_layout.addWidget(toggle_button, 0, 0, 2, 1)

        # Add checkboxes from 1 to 26, with 13 checkboxes per row
        for number in range(1, 27):
            checkbox = QCheckBox(str(number))
            checkbox.setStyleSheet(checkbox_style())

            # Calculate the row and column for each checkbox in the layout
            row = (number - 1) // 13 + 0  # Row starts at 1 after the button
            col = (number - 1) % 13 + 1  # Column ranges from 0 to 12

            wafer_layout.addWidget(checkbox, row, col)
            self.check_vars[number] = checkbox

        # Update checkbox styles based on subdirectories
        self.update_wafers()

        group_box.setLayout(wafer_layout)

        # Add the QGroupBox to the main layout
        self.layout.addWidget(group_box, 2, 0, 2, 4)

    def toggle_checkboxes(self):
        """Toggle the state of checkboxes updated in `update_wafers."""
        if not self.dirname:
            return  # Do nothing if no directory is specified

        # Get the list of subdirectories
        subdirs = [d for d in os.listdir(self.dirname) if
                   os.path.isdir(os.path.join(self.dirname, d))]

        # Filter checkboxes that correspond to the subdirectories
        relevant_checkboxes = [
            checkbox for number, checkbox in self.check_vars.items()
            if str(number) in subdirs
        ]

        # Determine whether to check or uncheck based on the first relevant checkbox
        all_checked = all(
            checkbox.isChecked() for checkbox in relevant_checkboxes)
        new_state = not all_checked  # Invert the state

        # Apply the new state to the relevant checkboxes
        for checkbox in relevant_checkboxes:
            checkbox.setChecked(new_state)

    def get_selected_wafer(self):
        """Retrieve a list of selected (checked) options from the checkboxes."""
        selected_options = []
        for number, checkbox in self.check_vars.items():
            if checkbox.isChecked():  # Check if the checkbox is checked
                selected_options.append(
                    str(number))  # Add the number to the list
        return selected_options

    def select_folder(self):
        """Select a parent folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select a Folder")

        if folder:
            self.dirname = folder
            max_characters = 20  # Set character limit

            # Truncate text if it exceeds the limit
            display_text = self.dirname if len(
                self.dirname) <= max_characters else self.dirname[
                                                     :max_characters] + '...'
            self.folder_path_label.setText(display_text)

    def select_recipe(self):
        """Select a JSON file"""
        file_filter = "JSON Files (*.json)"  # Filter for JSON files
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a JSON file",
                                                   "", file_filter)

        if file_path:
            self.recipe = file_path
            max_characters = 30  # Set character limit

            # Truncate text if it exceeds the limit
            display_text = self.recipe if len(
                self.recipe) <= max_characters else self.recipe[
                                                    :max_characters] + '...'
            self.recipe_path_label.setText(display_text)

    def selected_function_button(self):
        """Create a QGroupBox for data processing options."""

        # Create the QGroupBox
        group_box = QGroupBox("Options")
        group_box.setStyleSheet(group_box_style())

        # Set up layout for the QGroupBox
        group_layout = QGridLayout(group_box)

        # Create checkboxes

        # Add checkboxes to the layout
        group_layout.addWidget(self.check_boxes["Data processing"], 0, 0)
        group_layout.addWidget(self.check_boxes["Autoscale mapping"], 1, 0)
        group_layout.addWidget(self.check_boxes["Id. scale mapping"], 0, 1)
        group_layout.addWidget(self.check_boxes["Id. scale mapping (auto)"], 1, 1)
        group_layout.addWidget(self.check_boxes["Slot number"], 3, 0)
        group_layout.addWidget(self.check_boxes["Stats"], 3, 1)



        # Add the group box to the main layout
        self.layout.addWidget(group_box, 0, 4, 2, 1)

    def create_run_button(self):
        """Create a button to run data processing"""

        # Create the QPushButton
        run_button = QPushButton("Run data processing")
        run_button.setStyleSheet(run_button_style())
        run_button.clicked.connect(self.run_data_processing)
        run_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(run_button, 1, 5, 1, 2)

    def get_table_data(self):

        return self.settings_window.get_table_data()

    def get_selected_option(self):
        """Retrieve a list of selected (checked) options from the checkboxes."""
        selected_options = []
        for number, checkbox in self.check_vars.items():
            if checkbox.isChecked():  # Check if the checkbox is checked
                selected_options.append(
                    str(number))  # Add the number to the list
        return selected_options

    def run_data_processing(self):
        """Handles photoluminescence data processing and updates progress."""

        settings, input =self.settings_window.get_table_data()

        all_wafer, checked_wafer = self.get_wafer_states()
        print(all_wafer, checked_wafer)

        wafer_slot = self.check_boxes["Slot number"].isChecked()

        stats = self.check_boxes["Stats"].isChecked()

        if not self.dirname or not self.recipe :
            return


        all_radio_groups = [
            self.radio_buttons_wafer,
            self.radio_buttons_sample
        ]


        if not self.dirname or not any(
            radio_button.isChecked()
            for group in all_radio_groups
            for radio_button in group.values()
        ):
            return

        # # Initialize processing classes
        self.common_class = Common(self.dirname, settings, input)
        self.XRD_class = XRD(self.dirname, self.recipe, settings, input, cpu=4)

        total_steps=0
        if self.radio_buttons_wafer["Fitting"].isChecked():
            total_steps = 6
        elif self.radio_buttons_wafer["Create Database/Boxplot"].isChecked():
            total_steps = 2
        elif self.radio_buttons_wafer["Clean"].isChecked():
            total_steps = 1
        elif self.radio_buttons_wafer["Rename"].isChecked():
            total_steps = 1

        progress_dialog = QProgressDialog("Data processing in progress...",
                                          "Cancel", 0, total_steps, self)

        font = QFont()
        font.setPointSize(20)
        progress_dialog.setFont(font)

        progress_dialog.setWindowTitle("Processing")
        progress_dialog.setWindowModality(Qt.ApplicationModal)
        progress_dialog.setAutoClose(
            False)  # Ensure the dialog is not closed automatically
        progress_dialog.setCancelButton(None)  # Hide the cancel button
        progress_dialog.resize(400, 150)  # Set a larger size for the dialog

        progress_dialog.show()

        QApplication.processEvents()

        def execute_with_timer(task_name, task_function, *args, **kwargs):
            progress_dialog.setLabelText(task_name)
            QApplication.processEvents()
            task_function(*args, **kwargs)
                # Wafer-level operations
        if self.radio_buttons_wafer["Create Database/Boxplot"].isChecked():
            execute_with_timer("Create database", self.XRD_class.create_database, checked_wafer)
            execute_with_timer("Plot boxplot", self.common_class.plot_boxplot)

        if self.radio_buttons_wafer["Fitting"].isChecked():
            if self.check_boxes["Data processing"].isChecked():
                self.common_class.process_xo1_files()
                self.common_class.rename_txt_files()
                self.XRD_class.decomposition(checked_wafer)
                execute_with_timer("Create database", self.XRD_class.create_database, checked_wafer)
                execute_with_timer("Plot boxplot", self.common_class.plot_boxplot)
                execute_with_timer("Plot spectrum", self.common_class.plot_spectrum, checked_wafer)
                execute_with_timer("Stats files", self.common_class.stats)

            if self.check_boxes["Autoscale mapping"].isChecked():
                execute_with_timer("Plot mapping", self.XRD_class.plot, slot_number=wafer_slot, identical=False, wafers=checked_wafer, stats=stats)
                self.common_class.create_image_grid(zscale='Auto')
            if self.check_boxes["Id. scale mapping"].isChecked():
                execute_with_timer("Plot mapping ID scale", self.XRD_class.plot, slot_number=wafer_slot, identical='Manual', wafers=checked_wafer, stats=stats)
                self.common_class.create_image_grid(zscale='Identical')
            if self.check_boxes["Id. scale mapping (auto)"].isChecked():
                execute_with_timer("Plot mapping ID scale", self.XRD_class.plot, slot_number=wafer_slot, identical='Auto', wafers=checked_wafer, stats=stats)
                self.common_class.create_image_grid(zscale='Identical')

        if self.radio_buttons_wafer["Clean"].isChecked():
            execute_with_timer("Cleaning of folders", self.common_class.reboot, checked_wafer)
            self.update_wafers()

        if self.radio_buttons_wafer["Rename"].isChecked():
            self.common_class.process_xo1_files()
            self.common_class.rename_txt_files()

        # Sample-level operations
        if self.radio_buttons_sample["Clean"].isChecked():
            execute_with_timer("Cleaning of folders", self.common_class.reboot_sample)
            self.update_wafers()

        if self.radio_buttons_sample["Fitting"].isChecked():
            self.common_class.process_xo1_files()
            self.common_class.rename_txt_files()
            self.XRD_class.decomposition_sample()
            execute_with_timer("Create database", self.XRD_class.create_database_sample)
            execute_with_timer("Plot spectrum", self.common_class.plot_spectrum_sample)
            execute_with_timer("Plot graphes", self.common_class.plot_columns)


        progress_dialog.close()