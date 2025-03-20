from PySide6.QtCore import Qt

class StyleHelper:
    @staticmethod
    def apply_widget_style(widget, extra=""):
        widget.setStyleSheet(f"font-family: Roboto; font-size: 14px; {extra}")

    @staticmethod
    def apply_button_style(button, color="#ffeb3b", extra=""):
        button.setStyleSheet(f"background-color: {color}; color: #333; padding: 8px; border-radius: 5px; border: none; font-family: Roboto; font-size: 14px; {extra}")

    @staticmethod
    def apply_title_style(button):
        button.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffcc00; padding: 5px; border: 2px solid #ffd700; border-radius: 5px; background: none; max-width: 300px; font-family: Roboto;")

    @staticmethod
    def apply_header_style(label):
        label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff; background-color: #ffcc00; padding: 8px; border-radius: 10px; border: 2px solid #ffd700; font-family: Roboto;")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(40)
        label.setFixedWidth(780)