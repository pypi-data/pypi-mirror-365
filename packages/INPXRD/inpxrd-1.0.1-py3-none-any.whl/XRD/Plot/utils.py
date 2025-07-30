"""Function to create the savebutton or to clean sur frame_layout (left)"""
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QPushButton, QFileDialog)
from PyQt5.QtGui import QPainter, QPixmap, QImage
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Plot.style_plot import save_button_style


def ouvrir_image(dirname, numbers_str, x, y, image_raman):
    """
    To open image in the right frame (if image are available)
    """

    dir_raman = rf'{dirname}/{numbers_str}/Spectra/{x}_{y}_fitted.png'

    try:
        image = Image.open(dir_raman)
        image = image.resize((600, 250))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 24)
        draw.text((70, 10), f"Wafer {numbers_str} - {x}/{y}", fill="black",
                  font=font)
        image_data = image.convert("RGB")
        qimage = QImage(image_data.tobytes(), image_data.width,
                        image_data.height, image_data.width * 3,
                        QImage.Format_RGB888)

        img = QPixmap.fromImage(qimage)
        image_raman.setPixmap(img)
    except (FileNotFoundError, IOError):
        print(f"Image {dir_raman} non trouvée ou erreur lors de l'ouverture.")


def create_savebutton(layout, frame_left, frame_right):
    """Create a save button to capture and save specific
    frames as a combined image."""

    def save_image():
        """Capture and save specific frames as a combined image."""
        screen_left = frame_left.grab()
        screen_right = frame_right.grab()

        # Get the file path to save the combined image
        file_name, _ = QFileDialog.getSaveFileName(None,
                                                   "Save Combined Frame Screenshot",
                                                   "",
                                                   "PNG Files (*.png);;All Files (*)")

        if file_name:
            combined_width = screen_left.width() + screen_right.width()
            combined_height = max(screen_left.height(), screen_right.height())
            combined_pixmap = QPixmap(combined_width, combined_height)

            # Fill the combined QPixmap with a white background
            combined_pixmap.fill(Qt.white)

            painter = QPainter(combined_pixmap)
            painter.drawPixmap(0, 0, screen_left)
            painter.drawPixmap(screen_left.width(), 0, screen_right)
            painter.end()

            # Save the combined image
            combined_pixmap.save(file_name, "PNG")

    # Add the save button directly to the layout
    save_button = QPushButton("Screenshot")
    save_button.setStyleSheet(save_button_style())
    save_button.clicked.connect(save_image)
    layout.addWidget(save_button, 8, 0, 1, 7)


def clear_frame(frame_left_layout):
    """Clear all widgets and layouts from the given frame_left_layout
    and reset images and text labels."""
    for i in reversed(range(frame_left_layout.count())):
        item = frame_left_layout.itemAt(i)
        if item.layout():
            clear_layout(item.layout())
            frame_left_layout.removeItem(item)
        elif item.widget():
            widget = item.widget()
            widget.deleteLater()

    # Close any open Matplotlib figures
    for fig in plt.get_fignums():
        plt.close(fig)


def clear_layout(layout):
    """Recursively clear all widgets and sub-layouts inside a given layout."""
    while layout.count():
        item = layout.takeAt(0)
        if item.layout():
            clear_layout(item.layout())
        elif item.widget():
            item.widget().deleteLater()
