"""
GUI for data visualization
"""

import sys
import multiprocessing
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from PyQt5.QtCore import QTimer
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Layout.main_window_att import LayoutFrame
from Layout.create_button import ButtonFrame
from Layout.settings import SettingsWindow
from Plot.frame_attributes import PlotFrame

class MainWindow(QWidget):
    """Main window for data visualization"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("XRD")
        self.setStyleSheet("background-color: #F5F5F5;")

        # Create the main layout (canvas_layout)
        self.canvas_widget = QWidget(self)
        self.canvas_layout = QGridLayout(self.canvas_widget)

        # Use LayoutFrame for layout configuration
        self.layout_frame = LayoutFrame(self)
        self.layout_frame.setup_layout(self.canvas_widget, self.canvas_layout)

        self.button_frame = ButtonFrame(self.canvas_layout)
        self.plot_frame = PlotFrame(self.canvas_layout, self.button_frame)

        # Set/adapt the maximum window size
        self.layout_frame.set_max_window_size()
        self.layout_frame.position_window_top_left()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.layout_frame.adjust_scroll_area_size)
        self.timer.start(200)

    def closeEvent(self, event):
        """Handle actions when the window is closed."""
        self.button_frame.save_recipe()  # Save recipe before closing
        super().closeEvent(event)


def main():
    """Launch GUI"""
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
