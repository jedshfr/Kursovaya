from PySide6.QtWidgets import QApplication
from main import MainWindow

app = QApplication([])
app.setStyleSheet("""
    QMainWindow, QDialog { background-color: #fff9e6; }
    QPushButton { background-color: #ffeb3b; color: #333; padding: 8px; border-radius: 5px; border: none; font-family: Roboto; font-size: 14px; }
    QPushButton:hover { background-color: #ffd700; }
    QLineEdit, QComboBox { padding: 5px; border: 1px solid #ffd700; border-radius: 5px; background-color: #fffde7; font-family: Roboto; font-size: 14px; }
    QLabel, QListWidget { font-family: Roboto; font-size: 14px; }
""")
window = MainWindow()
window.show()
app.exec()