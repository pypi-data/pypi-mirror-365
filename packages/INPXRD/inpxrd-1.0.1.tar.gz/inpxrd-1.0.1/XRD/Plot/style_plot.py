"""
module for the button styles
"""

def plot_button_style():
    return """
        QPushButton {
            font-size: 16px;
            background-color: #d4fcdc;  /* Vert clair */
            border: 2px solid #8c8c8c;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #a5d6a7;  /* Vert légèrement plus foncé */
        }
        """

def save_button_style():
    return """
        QPushButton {
            font-size: 16px;
            background-color: #e6ccff;  /* Light purple */
            border: 2px solid #8c8c8c;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #d1b3ff;  /* Slightly darker purple */
        }
    """


