from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from styles import StyleHelper

def load_photo(photo_data, photo_label, size=(300, 300)):
    if photo_data and isinstance(photo_data, bytes):
        pixmap = QPixmap()
        if pixmap.loadFromData(photo_data):
            photo_label.setPixmap(pixmap.scaled(*size, Qt.KeepAspectRatio))
        else:
            photo_label.setText("Ошибка загрузки фото")
            StyleHelper.apply_widget_style(photo_label, "font-size: 16px;")
    else:
        photo_label.setText("Нет фото")
        StyleHelper.apply_widget_style(photo_label, "font-size: 16px;")
    photo_label.setAlignment(Qt.AlignCenter)

def select_photo(parent, photo_label, size=(300, 300)):
    file_name, _ = QFileDialog.getOpenFileName(parent, "Выбрать фото", "", "Images (*.png *.jpg *.jpeg)")
    if file_name:
        with open(file_name, 'rb') as f:
            photo_data = f.read()
        pixmap = QPixmap()
        if pixmap.loadFromData(photo_data):
            photo_label.setPixmap(pixmap.scaled(*size, Qt.KeepAspectRatio))
        return photo_data
    return None

def show_message(title, text, msg_type="info"):
    msg = QMessageBox()
    if msg_type == "info":
        msg.information(None, title, text)
    elif msg_type == "warning":
        msg.warning(None, title, text)
    elif msg_type == "question":
        return msg.question(None, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes