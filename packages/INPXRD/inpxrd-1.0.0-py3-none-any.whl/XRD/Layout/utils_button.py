"""
module description
"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPushButton, QSizePolicy
import tkinter as tk
from fitspy.apps.tkinter.gui import Appli
from Layout.style import open_fitspy_button_style

def create_fitspy_button(layout):
    """
    Création du bouton pour ouvrir l'application Fitspy.
    """

    def open_fitspy():
        """
        Ouvre la fenêtre Fitspy.
        """
        root = tk.Tk()
        app = Appli(root)
        root.mainloop()

    btn_open_fitspy = QPushButton("Fitspy")
    btn_open_fitspy.setStyleSheet(open_fitspy_button_style())
    btn_open_fitspy.clicked.connect(open_fitspy)
    btn_open_fitspy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    layout.addWidget(btn_open_fitspy, 0, 6, 1, 1)





