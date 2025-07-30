import os
import json
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (QPushButton, QLabel, QGroupBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QDialog, QFileDialog, QHBoxLayout,
    QLineEdit, QCheckBox, QVBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

class SettingsWindow(QDialog):
    data_updated = pyqtSignal()  # Signal emitted when data is updated

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.resize(1200, 800)

        # Get the user's home directory
        self.user_folder = os.path.expanduser("~")

        # Define the folder "Raman" and the file to store settings
        self.new_folder = os.path.join(self.user_folder, "Raman")
        self.data_file = os.path.join(self.new_folder, "settings_data.json")
        self.data = []  # Structure to store table data
        self.input_values = {}

        # Set up the UI layout
        self.layout = QHBoxLayout()  # Use QHBoxLayout for side-by-side layout
        self.setLayout(self.layout)

        # Create a container layout for the table and buttons (Vertical layout for table and buttons)
        self.table_layout = QVBoxLayout()

        # Create and add the table to the layout
        self.create_table()

        # Create the input fields section
        self.create_input_fields()

        # Create and add the buttons below the table
        self.create_buttons()

        # Load data from the settings file
        self.load_data()

        # Add the table layout to the main layout
        self.layout.addLayout(self.table_layout)

    def load_json_file(self):
        """Load settings from a JSON file and update the settings window."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)", options=options
        )

        if file_path:
            try:
                with open(file_path, "r") as file:
                    saved_data = json.load(file)
                    # Reset the table and data
                    self.table.setRowCount(0)  # Clear the table
                    self.data = []  # Reset the internal structure

                    table_data = saved_data.get("table_data", [])
                    for row_data in table_data:
                        self.add_row(
                            row_data.get("Peak", ""), row_data.get("Ylabel", ""),
                            row_data.get("Filename", ""), row_data.get("Min", ""),
                            row_data.get("Max", ""), row_data.get("Threshold", False),
                            row_data.get("Boxplot", False), update_data=False
                        )
                    self.data = table_data

                    # Load input field values
                    self.input_values = saved_data.get("input_values")
                    self.wafer_size_input.setText(self.input_values.get("Wafer Size"))
                    self.edge_exclusion_input.setText(self.input_values.get("Edge Exclusion"))
                    self.spectra_xmin_input.setText(self.input_values.get("Spectra xmin"))
                    self.spectra_xmax_input.setText(self.input_values.get("Spectra xmax"))
                    self.spectra_ymin_input.setText(self.input_values.get("Spectra ymin"))
                    self.spectra_ymax_input.setText(self.input_values.get("Spectra ymax"))
                    self.spectra_xlabel_input.setText(self.input_values.get("Xlabel"))
                    self.spectra_ylabel_input.setText(self.input_values.get("Ylabel"))

                    print("Data loaded successfully:", self.data, self.input_values)
            except FileNotFoundError:
                print("No previous data found. Starting fresh.")
                self.data = []
            except Exception as e:
                print(f"Error loading data: {e}")
                self.data = []

    def create_table(self):
        """Create the settings table."""
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Total 7 columns
        self.table.setHorizontalHeaderLabels(["Peak", "Ylabel", "Filename", "Min", "Max", "Threshold", "Boxplot"])
        self.table.setMinimumHeight(200)
        self.table.setMinimumWidth(800)

        self.table.blockSignals(True)

        # Apply styling to increase text size
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 16px;
                text-align: center;
            }
            QTableWidget::item {
                padding: 5px;
                text-align: center;
            }
            QHeaderView::section {
                font-size: 16px;
                background-color: #f2f2f2;
                text-align: center;
            }
        """)

        # Populate the table with existing data
        for row_data in self.data:
            self.add_row(
                row_data.get("Peak", ""), row_data.get("Ylabel", ""),
                row_data.get("Filename", ""), row_data.get("Min", ""),
                row_data.get("Max", ""), row_data.get("Threshold", False),
                row_data.get("Boxplot", False), update_data=False
            )

        self.table.blockSignals(False)
        self.table.itemChanged.connect(self.update_data)
        self.table_layout.addWidget(self.table)

    def remove_selected_row(self):
        """Remove the currently selected row."""
        current_row = self.table.currentRow()
        if current_row != -1:
            self.table.removeRow(current_row)
            del self.data[current_row]

    def create_buttons(self):
        """Create buttons to add and remove rows, and load/save JSON."""
        add_button = QPushButton("Add Row")
        remove_button = QPushButton("Remove Selected Row")
        load_button = QPushButton("Load JSON")
        save_button = QPushButton("Save JSON File")

        button_style = """
            QPushButton {
                font-size: 18px;
                background-color: #f0f0f0;
                color: black;
                border: 2px solid black;
                border-radius: 10px;
                padding: 10px 20px;
                min-width: 150px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Apply styling to buttons
        add_button.setStyleSheet(button_style)
        remove_button.setStyleSheet(button_style)
        load_button.setStyleSheet(button_style)
        save_button.setStyleSheet(button_style)

        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_selected_row)
        load_button.clicked.connect(self.load_json_file)
        save_button.clicked.connect(self.save_json_file)

        # Add buttons to the layout under the table
        self.table_layout.addWidget(add_button)
        self.table_layout.addWidget(remove_button)
        self.table_layout.addWidget(load_button)
        self.table_layout.addWidget(save_button)

    def save_json_file(self):
        """Save settings to a JSON file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)", options=options
        )
        if file_path:
            # Retrieve input field values
            input_values = {
                "Wafer Size": self.wafer_size_input.text(),
                "Edge Exclusion": self.edge_exclusion_input.text(),
                "Spectra xmin": self.spectra_xmin_input.text(),
                "Spectra xmax": self.spectra_xmax_input.text(),
                "Spectra ymin": self.spectra_ymin_input.text(),
                "Spectra ymax": self.spectra_ymax_input.text(),
                "Xlabel": self.spectra_xlabel_input.text(),
                "Ylabel": self.spectra_ylabel_input.text()
            }

            # Retrieve table data
            table_data = []
            for row in range(self.table.rowCount()):
                peak = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                ylabel = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                filename = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
                min_value = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
                max_value = self.table.item(row, 4).text() if self.table.item(row, 4) else ""

                threshold_checkbox = self.table.cellWidget(row, 5)
                boxplot_checkbox = self.table.cellWidget(row, 6)
                threshold_checked = threshold_checkbox.isChecked() if isinstance(threshold_checkbox, QCheckBox) else False
                boxplot_checked = boxplot_checkbox.isChecked() if isinstance(boxplot_checkbox, QCheckBox) else False

                table_data.append({
                    "Peak": peak,
                    "Ylabel": ylabel,
                    "Filename": filename,
                    "Min": min_value,
                    "Max": max_value,
                    "Threshold": threshold_checked,
                    "Boxplot": boxplot_checked
                })

            # Save data to the JSON file
            data_to_save = {
                "table_data": table_data,
                "input_values": input_values
            }

            with open(file_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)
            print("Data saved successfully:", data_to_save)

    def create_input_fields(self):
        """Create input fields for wafer size and spectra limits inside a QGroupBox."""
        self.input_group_box = QGroupBox("Input Fields")
        self.input_layout = QVBoxLayout()

        def create_input_row(label_text, input_widget):
            row_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    color: black;
                    margin-right: 10px;
                }
            """)
            input_widget.setStyleSheet("""
                QLineEdit {
                    font-size: 18px;
                    color: black;
                    padding: 10px;
                    min-width: 200px;
                }
            """)
            row_layout.addWidget(label)
            row_layout.addWidget(input_widget)
            return row_layout

        self.wafer_size_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Wafer Size (mm):", self.wafer_size_input))

        self.edge_exclusion_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Edge Exclusion (mm):", self.edge_exclusion_input))

        self.spectra_xmin_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Spectra xmin:", self.spectra_xmin_input))

        self.spectra_xmax_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Spectra xmax:", self.spectra_xmax_input))

        self.spectra_ymin_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Spectra ymin:", self.spectra_ymin_input))

        self.spectra_ymax_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Spectra ymax:", self.spectra_ymax_input))

        self.spectra_xlabel_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Xlabel:", self.spectra_xlabel_input))

        self.spectra_ylabel_input = QLineEdit()
        self.input_layout.addLayout(create_input_row("Ylabel:", self.spectra_ylabel_input))

        self.input_group_box.setLayout(self.input_layout)
        self.layout.addWidget(self.input_group_box)

    def add_row(self, peak=None, ylabel="", filename="", min_value="", max_value="", is_checked=False, boxplot_checked=False, update_data=True):
        """Add a new row to the table with default values."""
        if peak is None:
            peak = ""

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        peak_item = QTableWidgetItem(str(peak))
        ylabel_item = QTableWidgetItem(str(ylabel))
        filename_item = QTableWidgetItem(str(filename))
        min_item = QTableWidgetItem(str(min_value))
        max_item = QTableWidgetItem(str(max_value))

        self.table.setItem(row_position, 0, peak_item)
        self.table.setItem(row_position, 1, ylabel_item)
        self.table.setItem(row_position, 2, filename_item)
        self.table.setItem(row_position, 3, min_item)
        self.table.setItem(row_position, 4, max_item)

        checkbox = QCheckBox()
        checkbox.setChecked(bool(is_checked))
        checkbox.stateChanged.connect(lambda state, row=row_position: self.handle_checkbox_state_change(state, row))
        self.table.setCellWidget(row_position, 5, checkbox)

        boxplot_checkbox = QCheckBox()
        boxplot_checkbox.setChecked(bool(boxplot_checked))
        boxplot_checkbox.stateChanged.connect(lambda state, row=row_position: self.handle_boxplot_checkbox_state_change(state, row))
        self.table.setCellWidget(row_position, 6, boxplot_checkbox)

        if update_data:
            self.data.append({
                "Peak": peak or "",
                "Ylabel": ylabel or "",
                "Filename": filename or "",
                "Min": min_value or "",
                "Max": max_value or "",
                "Threshold": bool(is_checked),
                "Boxplot": bool(boxplot_checked),
            })

        self.table.itemChanged.connect(self.update_data)

    def handle_boxplot_checkbox_state_change(self, state, current_row):
        """Handle state change for the 'Boxplot' checkbox."""
        is_checked = state == Qt.Checked
        if current_row < len(self.data):
            self.data[current_row]["Boxplot"] = is_checked
            print(f"Boxplot updated for row {current_row}: {is_checked}")

    def handle_checkbox_state_change(self, state, current_row):
        """Ensure only one checkbox is selected at a time."""
        if state == Qt.Checked:
            for row in range(self.table.rowCount()):
                if row != current_row:
                    checkbox = self.table.cellWidget(row, 5)
                    checkbox.blockSignals(True)
                    checkbox.setChecked(False)
                    checkbox.blockSignals(False)

            for i, row_data in enumerate(self.data):
                row_data["Threshold"] = (i == current_row)

    def update_data(self, item):
        """Update the data structure when a table cell value or input field value changes."""
        if isinstance(item, QTableWidgetItem):
            row = item.row()
            column = item.column()

            if row >= len(self.data):
                return

            if column == 0:
                self.data[row]["Peak"] = item.text()
            elif column == 1:
                self.data[row]["Ylabel"] = item.text()
            elif column == 2:
                self.data[row]["Filename"] = item.text()
            elif column == 3:
                self.data[row]["Min"] = item.text()
            elif column == 4:
                self.data[row]["Max"] = item.text()

        elif isinstance(item, QLineEdit):
            self.input_values = {
                "Wafer Size": self.wafer_size_input.text(),
                "Edge Exclusion": self.edge_exclusion_input.text(),
                "Spectra xmin": self.spectra_xmin_input.text(),
                "Spectra xmax": self.spectra_xmax_input.text(),
                "Spectra ymin": self.spectra_ymin_input.text(),
                "Spectra ymax": self.spectra_ymax_input.text(),
                "Xlabel": self.spectra_xlabel_input.text(),
                "Ylabel": self.spectra_ylabel_input.text(),
            }

        for row in range(self.table.rowCount()):
            if row < len(self.data):
                threshold_checkbox = self.table.cellWidget(row, 5)
                boxplot_checkbox = self.table.cellWidget(row, 6)

                if isinstance(threshold_checkbox, QCheckBox):
                    self.data[row]["Threshold"] = threshold_checkbox.isChecked()
                if isinstance(boxplot_checkbox, QCheckBox):
                    self.data[row]["Boxplot"] = boxplot_checkbox.isChecked()

        self.save_data()

    def closeEvent(self, event):
        """Save data to a file when the dialog is closed."""
        self.save_data()
        self.data_updated.emit()
        super().closeEvent(event)

    def save_data(self):
        """Save the table data and input field values to a JSON file."""
        if self.data_file and os.path.dirname(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        self.input_values = {
            "Wafer Size": self.wafer_size_input.text(),
            "Edge Exclusion": self.edge_exclusion_input.text(),
            "Spectra xmin": self.spectra_xmin_input.text(),
            "Spectra xmax": self.spectra_xmax_input.text(),
            "Spectra ymin": self.spectra_ymin_input.text(),
            "Spectra ymax": self.spectra_ymax_input.text(),
            "Xlabel": self.spectra_xlabel_input.text(),
            "Ylabel": self.spectra_ylabel_input.text()
        }

        data_to_save = {
            "table_data": self.data,
            "input_values": self.input_values
        }

        try:
            with open(self.data_file, "w") as file:
                json.dump(data_to_save, file, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        """Load the table data and input field values from the JSON file."""
        try:
            with open(self.data_file, "r") as file:
                saved_data = json.load(file)
                table_data = saved_data.get("table_data", [])
                for row_data in table_data:
                    self.add_row(
                        row_data.get("Peak", ""), row_data.get("Ylabel", ""),
                        row_data.get("Filename", ""), row_data.get("Min", ""),
                        row_data.get("Max", ""), row_data.get("Threshold", False),
                        row_data.get("Boxplot", False), update_data=False
                    )
                self.data = table_data

                self.input_values = saved_data.get("input_values")
                self.wafer_size_input.setText(self.input_values.get("Wafer Size"))
                self.edge_exclusion_input.setText(self.input_values.get("Edge Exclusion"))
                self.spectra_xmin_input.setText(self.input_values.get("Spectra xmin"))
                self.spectra_xmax_input.setText(self.input_values.get("Spectra xmax"))
                self.spectra_ymin_input.setText(self.input_values.get("Spectra ymin"))
                self.spectra_ymax_input.setText(self.input_values.get("Spectra ymax"))
                self.spectra_xlabel_input.setText(self.input_values.get("Xlabel"))
                self.spectra_ylabel_input.setText(self.input_values.get("Ylabel"))

            print("Data loaded successfully:", self.data, self.input_values)
        except FileNotFoundError:
            print("No previous data found. Starting fresh.")
            self.data = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = []

    def get_table_data(self):
        """Get the current data from the table as a list of dictionaries."""
        if self.input_values is not None:
            return self.data, self.input_values


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings_window = SettingsWindow()
    settings_window.show()
    sys.exit(app.exec_())

