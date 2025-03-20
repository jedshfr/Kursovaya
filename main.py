from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, 
                              QLabel, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QTableWidget, 
                              QTableWidgetItem, QDateEdit, QFileDialog)
from PySide6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PySide6.QtCore import Qt, QDate
from models import Car, Driver, Status, ExpensesCar, ServiceCar, TypeWork, TypeExpenses, Address, session
from styles import StyleHelper
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.lib.styles import getSampleStyleSheet
from utils import load_photo, select_photo, show_message

# Класс карточки автомобиля
class CarCard(QWidget):
    def __init__(self, car, parent=None):
        super().__init__(parent)
        self.car = car
        self.parent_widget = parent
        StyleHelper.apply_widget_style(self, "background-color: #fff9e6; border-radius: 15px; padding: 15px; border: 2px solid #ffd700;")
        self.setFixedSize(750, 400)

        self.main_layout = QHBoxLayout()
        
        self.info_layout = QVBoxLayout()
        self.info_widget = QWidget()
        self.info_sub_layout = QVBoxLayout(self.info_widget)
        self.info = QLabel(f"Номер: {car.number}\nПробег: {car.mileage} км\nГод: {car.year}\nСтатус: {car.status.status}")
        self.driver = car.driver
        self.driver_info = QLabel(f"Водитель: {self.driver.surname} {self.driver.name} {self.driver.middle_name}" if self.driver else "Водитель: Не назначен")
        self.driver_info.setCursor(Qt.PointingHandCursor)
        self.driver_info.mousePressEvent = self.show_driver_info
        StyleHelper.apply_widget_style(self.info)
        StyleHelper.apply_widget_style(self.driver_info)
        self.info_sub_layout.addWidget(self.info)
        self.info_sub_layout.addWidget(self.driver_info)
        self.info_layout.addWidget(self.info_widget, alignment=Qt.AlignLeft)

        self.edit_btn = QPushButton("Редактировать")
        StyleHelper.apply_button_style(self.edit_btn, extra="max-width: 150px;")
        self.info_layout.addWidget(self.edit_btn, alignment=Qt.AlignHCenter)
        self.main_layout.addLayout(self.info_layout)

        self.right_layout = QVBoxLayout()
        self.photo_label = QLabel()
        load_photo(self.car.photo, self.photo_label)
        self.right_layout.addWidget(self.photo_label, alignment=Qt.AlignCenter)

        self.nav_layout = QHBoxLayout()
        self.left_btn = QPushButton("Предыдущий")
        self.right_btn = QPushButton("Следующий")
        StyleHelper.apply_button_style(self.left_btn, extra="min-width: 120px;")
        StyleHelper.apply_button_style(self.right_btn, extra="min-width: 120px;")
        self.nav_layout.addWidget(self.left_btn)
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.right_btn)
        self.right_layout.addLayout(self.nav_layout)
        self.main_layout.addLayout(self.right_layout)

        self.main_layout.setStretch(0, 4)
        self.main_layout.setStretch(1, 6)
        self.setLayout(self.main_layout)

    # Обновление данных карточки
    def update_card(self):
        self.car = session.query(Car).get(self.car.car_id)
        self.info.setText(f"Номер: {self.car.number}\nПробег: {self.car.mileage} км\nГод: {self.car.year}\nСтатус: {self.car.status.status}")
        self.driver = self.car.driver
        self.driver_info.setText(f"Водитель: {self.driver.surname} {self.driver.name} {self.driver.middle_name}" if self.driver else "Водитель: Не назначен")
        load_photo(self.car.photo, self.photo_label)

    def show_driver_info(self, event):
        if self.driver:
            dialog = DriverDetailsDialog(self.driver, self.parent_widget)
            dialog.exec()

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет автопарка")
        self.setWindowIcon(QIcon("car_icon.png"))
        self.setFixedSize(800, 650)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.header_label = QLabel("Автомобили")
        StyleHelper.apply_header_style(self.header_label)
        self.layout.addWidget(self.header_label, alignment=Qt.AlignTop)

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        StyleHelper.apply_widget_style(self.search_input)
        self.search_input.setPlaceholderText("Поиск по номеру или названию")
        self.search_btn = QPushButton("Найти")
        StyleHelper.apply_button_style(self.search_btn, extra="min-width: 100px;")
        self.search_btn.clicked.connect(self.search_car)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_btn)
        self.layout.addLayout(self.search_layout)

        self.car_title = QPushButton("")
        StyleHelper.apply_title_style(self.car_title)
        self.car_title.clicked.connect(self.show_service_expenses)
        self.layout.addWidget(self.car_title, alignment=Qt.AlignCenter)

        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_container.setFixedSize(750, 450)
        self.cars = session.query(Car).filter_by(is_archived=False).all()
        self.current_car_index = 0
        self.load_current_car()
        self.layout.addWidget(self.card_container, alignment=Qt.AlignCenter)

        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить автомобиль")
        self.archive_btn = QPushButton("Архив")
        StyleHelper.apply_button_style(self.add_btn, extra="min-width: 200px;")
        StyleHelper.apply_button_style(self.archive_btn, extra="min-width: 200px;")
        self.add_btn.clicked.connect(self.add_car)
        self.archive_btn.clicked.connect(self.show_archive)
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.archive_btn)
        self.layout.addLayout(self.btn_layout)

        self.layout.addStretch()

    # Загрузка текущей карточки автомобиля
    def load_current_car(self):
        for i in reversed(range(self.card_layout.count())):
            self.card_layout.itemAt(i).widget().setParent(None)
        if self.cars and 0 <= self.current_car_index < len(self.cars):
            self.card = CarCard(self.cars[self.current_car_index], self)
            self.card_layout.addWidget(self.card, alignment=Qt.AlignCenter)
            self.car_title.setText(f"{self.cars[self.current_car_index].mark} {self.cars[self.current_car_index].model}")
            self.card.left_btn.clicked.connect(self.prev_car)
            self.card.right_btn.clicked.connect(self.next_car)
            self.card.edit_btn.clicked.connect(lambda: self.edit_car(self.card))
        else:
            label = QLabel("Нет автомобилей")
            StyleHelper.apply_widget_style(label)
            self.card_layout.addWidget(label, alignment=Qt.AlignCenter)
            self.car_title.setText("Нет автомобилей")

    def prev_car(self):
        if self.cars:
            self.current_car_index = (self.current_car_index - 1) % len(self.cars)
            self.load_current_car()

    def next_car(self):
        if self.cars:
            self.current_car_index = (self.current_car_index + 1) % len(self.cars)
            self.load_current_car()

    def add_car(self):
        dialog = AddCarDialog()
        if dialog.exec():
            self.cars = session.query(Car).filter_by(is_archived=False).all()
            self.current_car_index = len(self.cars) - 1
            self.load_current_car()

    def edit_car(self, card):
        dialog = EditCarDialog(card.car)
        if dialog.exec():
            self.cars = session.query(Car).filter_by(is_archived=False).all()
            self.current_car_index = self.cars.index(session.query(Car).get(card.car.car_id)) if card.car in self.cars else 0
            self.load_current_car()

    def show_service_expenses(self):
        if self.cars and 0 <= self.current_car_index < len(self.cars):
            dialog = CarServiceExpensesDialog(self.cars[self.current_car_index])
            dialog.exec()

    def show_archive(self):
        dialog = ArchiveDialog(self)
        dialog.exec()

    def search_car(self):
        query = self.search_input.text().strip().lower()
        if not query:
            show_message("Ошибка", "Введите запрос для поиска!", "warning")
            return
        for i, car in enumerate(self.cars):
            if query in car.number.lower() or query in f"{car.mark} {car.model}".lower():
                self.current_car_index = i
                self.load_current_car()
                return
        show_message("Увы", "Автомобиль не найден.")

# Базовый класс для диалогов
class BaseDialog(QDialog):
    def __init__(self, title, icon="car_icon.png", size=(700, 500)):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self.setMinimumSize(*size)
        self.main_layout = QVBoxLayout()
        self.content_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.photo_widget = QWidget()
        StyleHelper.apply_widget_style(self.photo_widget, "background-color: #fff9e6; border-radius: 15px; padding: 15px; border: 2px solid #ffd700;")
        self.photo_layout = QVBoxLayout(self.photo_widget)
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(300, 300)
        self.photo_layout.addWidget(self.photo_label, alignment=Qt.AlignCenter)
        self.right_layout.addWidget(self.photo_widget, alignment=Qt.AlignCenter)
        self.close_btn = QPushButton("Закрыть")
        StyleHelper.apply_button_style(self.close_btn)
        self.close_btn.clicked.connect(self.reject)
        self.right_layout.addWidget(self.close_btn, alignment=Qt.AlignBottom | Qt.AlignRight)
        self.right_layout.addStretch()

    def setup_layout(self, title_text):
        self.title_btn = QPushButton(title_text)
        StyleHelper.apply_title_style(self.title_btn)
        self.main_layout.addWidget(self.title_btn, alignment=Qt.AlignCenter)
        self.content_layout.addLayout(self.left_layout)
        self.content_layout.addLayout(self.right_layout)
        self.content_layout.setStretch(0, 1)
        self.content_layout.setStretch(1, 2)
        self.main_layout.addLayout(self.content_layout)
        self.setLayout(self.main_layout)

# Диалог добавления автомобиля
class AddCarDialog(BaseDialog):
    def __init__(self):
        super().__init__("Добавление автомобиля", size=(700, 500))
        self.setup_ui()

    def setup_ui(self):
        self.setup_layout("Новый автомобиль")
        self.inputs = {
            "mark": QLineEdit(),
            "model": QLineEdit(),
            "number": QLineEdit(),
            "mileage": QLineEdit(),
            "year": QLineEdit()
        }
        for input_field in self.inputs.values():
            StyleHelper.apply_widget_style(input_field)
        self.inputs["mileage"].setValidator(QIntValidator(0, 999999, self))
        self.inputs["year"].setValidator(QIntValidator(1900, 2100, self))

        self.left_layout.addWidget(QLabel("Марка:"))
        self.left_layout.addWidget(self.inputs["mark"])
        self.left_layout.addWidget(QLabel("Модель:"))
        self.left_layout.addWidget(self.inputs["model"])
        self.left_layout.addWidget(QLabel("Номер:"))
        self.left_layout.addWidget(self.inputs["number"])
        self.left_layout.addWidget(QLabel("Пробег:"))
        self.left_layout.addWidget(self.inputs["mileage"])
        self.left_layout.addWidget(QLabel("Год:"))
        self.left_layout.addWidget(self.inputs["year"])

        self.status_combo = QComboBox()
        StyleHelper.apply_widget_style(self.status_combo)
        for status in session.query(Status).all():
            self.status_combo.addItem(status.status, status.status_id)
        self.left_layout.addWidget(QLabel("Статус:"))
        self.left_layout.addWidget(self.status_combo)

        self.driver_combo = QComboBox()
        StyleHelper.apply_widget_style(self.driver_combo)
        self.driver_combo.addItem("Без водителя", None)
        for driver in session.query(Driver).all():
            self.driver_combo.addItem(f"{driver.surname} {driver.name}", driver.driver_id)
        self.left_layout.addWidget(QLabel("Водитель:"))
        self.left_layout.addWidget(self.driver_combo)

        self.photo_btn = QPushButton("Выбрать фото")
        StyleHelper.apply_button_style(self.photo_btn)
        self.photo_btn.clicked.connect(self.select_photo)
        self.left_layout.addWidget(self.photo_btn)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        StyleHelper.apply_button_style(self.save_btn)
        self.save_btn.clicked.connect(self.save_car)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.save_btn)
        self.left_layout.addLayout(self.btn_layout)

        load_photo(None, self.photo_label)

    def select_photo(self):
        self.photo_data = select_photo(self, self.photo_label)

    def save_car(self):
        if not all(input_field.text() for input_field in self.inputs.values()):
            show_message("Ошибка", "Заполните все поля!", "warning")
            return
        new_car = Car(
            mark=self.inputs["mark"].text(),
            model=self.inputs["model"].text(),
            number=self.inputs["number"].text(),
            mileage=int(self.inputs["mileage"].text()),
            year=int(self.inputs["year"].text()),
            status_id=self.status_combo.currentData(),
            driver_id=self.driver_combo.currentData(),
            photo=self.photo_data if hasattr(self, "photo_data") else None,
            is_archived=False
        )
        session.add(new_car)
        session.commit()
        show_message("Успех", "Автомобиль успешно добавлен!")
        self.accept()

# Диалог редактирования автомобиля
class EditCarDialog(BaseDialog):
    def __init__(self, car):
        self.car = car
        super().__init__("Редактирование автомобиля", size=(700, 500))
        self.setup_ui()

    def setup_ui(self):
        self.setup_layout(f"{self.car.mark} {self.car.model}")
        self.inputs = {
            "mark": QLineEdit(self.car.mark or ""),
            "model": QLineEdit(self.car.model or ""),
            "number": QLineEdit(self.car.number or ""),
            "mileage": QLineEdit(str(self.car.mileage) if self.car.mileage else "0"),
            "year": QLineEdit(str(self.car.year) if self.car.year else "")
        }
        for input_field in self.inputs.values():
            StyleHelper.apply_widget_style(input_field)
        self.inputs["mileage"].setValidator(QIntValidator(0, 999999, self))
        self.inputs["year"].setValidator(QIntValidator(1900, 2100, self))

        self.left_layout.addWidget(QLabel("Марка:"))
        self.left_layout.addWidget(self.inputs["mark"])
        self.left_layout.addWidget(QLabel("Модель:"))
        self.left_layout.addWidget(self.inputs["model"])
        self.left_layout.addWidget(QLabel("Номер:"))
        self.left_layout.addWidget(self.inputs["number"])
        self.left_layout.addWidget(QLabel("Пробег:"))
        self.left_layout.addWidget(self.inputs["mileage"])
        self.left_layout.addWidget(QLabel("Год:"))
        self.left_layout.addWidget(self.inputs["year"])

        self.status_combo = QComboBox()
        StyleHelper.apply_widget_style(self.status_combo)
        for status in session.query(Status).all():
            self.status_combo.addItem(status.status, status.status_id)
        self.status_combo.setCurrentIndex(self.status_combo.findData(self.car.status_id))
        self.left_layout.addWidget(QLabel("Статус:"))
        self.left_layout.addWidget(self.status_combo)

        self.driver_combo = QComboBox()
        StyleHelper.apply_widget_style(self.driver_combo)
        self.driver_combo.addItem("Без водителя", None)
        for driver in session.query(Driver).all():
            self.driver_combo.addItem(f"{driver.surname} {driver.name}", driver.driver_id)
        self.driver_combo.setCurrentIndex(self.driver_combo.findData(self.car.driver_id))
        self.left_layout.addWidget(QLabel("Водитель:"))
        self.left_layout.addWidget(self.driver_combo)

        self.photo_btn = QPushButton("Заменить фото")
        StyleHelper.apply_button_style(self.photo_btn)
        self.photo_btn.clicked.connect(self.select_photo)
        self.left_layout.addWidget(self.photo_btn)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.delete_btn = QPushButton("Удалить")
        StyleHelper.apply_button_style(self.save_btn)
        StyleHelper.apply_button_style(self.delete_btn, color="#ff4444", extra="color: #fff;")
        self.save_btn.clicked.connect(self.save_car)
        self.delete_btn.clicked.connect(self.archive_car)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.left_layout.addLayout(self.btn_layout)

        load_photo(self.car.photo, self.photo_label)

    def select_photo(self):
        self.photo_data = select_photo(self, self.photo_label)

    def save_car(self):
        if not all(input_field.text() for input_field in self.inputs.values()):
            show_message("Ошибка", "Заполните все поля!", "warning")
            return
        self.car.mark = self.inputs["mark"].text()
        self.car.model = self.inputs["model"].text()
        self.car.number = self.inputs["number"].text()
        self.car.mileage = int(self.inputs["mileage"].text())
        self.car.year = int(self.inputs["year"].text())
        self.car.status_id = self.status_combo.currentData()
        self.car.driver_id = self.driver_combo.currentData()
        if hasattr(self, "photo_data"):
            self.car.photo = self.photo_data
        session.commit()
        show_message("Успех", "Изменения успешно сохранены!")
        self.accept()

    def archive_car(self):
        if show_message("Подтверждение", f"Действительно ли удалить автомобиль {self.car.mark} {self.car.model}?", "question"):
            self.car.is_archived = True
            session.commit()
            self.accept()

# Диалог информации о водителе
class DriverDetailsDialog(BaseDialog):
    def __init__(self, driver, parent=None):
        self.driver = driver
        self.parent_widget = parent
        super().__init__(f"Информация о водителе: {driver.surname} {driver.name}", size=(800, 800))
        self.setup_ui()

    def setup_ui(self):
        self.setup_layout(f"{self.driver.surname} {self.driver.name} {self.driver.middle_name or ''}")
        self.inputs = {
            "surname": QLineEdit(str(self.driver.surname or "")),
            "name": QLineEdit(str(self.driver.name or "")),
            "middle_name": QLineEdit(str(self.driver.middle_name or "")),
            "phone": QLineEdit(str(self.driver.phone or "")),
            "experience": QLineEdit(str(self.driver.experience) if self.driver.experience is not None else ""),
            "series": QLineEdit(str(self.driver.drivers_license_series or "")),
            "number": QLineEdit(str(self.driver.drivers_license_numbers or ""))
        }
        address = session.query(Address).get(self.driver.address_id) if self.driver.address_id else Address()
        self.address_inputs = {
            "region": QLineEdit(str(address.region or "")),
            "city": QLineEdit(str(address.city or "")),
            "street": QLineEdit(str(address.street or "")),
            "home": QLineEdit(str(address.home) if address.home is not None else ""),
            "index": QLineEdit(str(address.index) if address.index is not None else "")
        }
        for input_field in list(self.inputs.values()) + list(self.address_inputs.values()):
            StyleHelper.apply_widget_style(input_field)
            input_field.setReadOnly(True)
        self.inputs["phone"].setMaxLength(12)
        self.inputs["experience"].setValidator(QIntValidator(0, 100, self))
        self.inputs["series"].setValidator(QIntValidator(0, 9999, self))
        self.inputs["series"].setMaxLength(4)
        self.inputs["number"].setValidator(QIntValidator(0, 999999, self))
        self.inputs["number"].setMaxLength(6)
        self.address_inputs["home"].setValidator(QIntValidator(0, 9999, self))
        self.address_inputs["index"].setValidator(QIntValidator(0, 999999, self))
        self.left_layout.addWidget(QLabel("Фамилия:"))
        self.left_layout.addWidget(self.inputs["surname"])
        self.left_layout.addWidget(QLabel("Имя:"))
        self.left_layout.addWidget(self.inputs["name"])
        self.left_layout.addWidget(QLabel("Отчество:"))
        self.left_layout.addWidget(self.inputs["middle_name"])
        self.left_layout.addWidget(QLabel("Телефон:"))
        self.left_layout.addWidget(self.inputs["phone"])
        self.left_layout.addWidget(QLabel("Стаж:"))
        self.left_layout.addWidget(self.inputs["experience"])
        self.left_layout.addWidget(QLabel("Серия ВУ:"))
        self.left_layout.addWidget(self.inputs["series"])
        self.left_layout.addWidget(QLabel("Номер ВУ:"))
        self.left_layout.addWidget(self.inputs["number"])
        self.left_layout.addWidget(QLabel("Регион:"))
        self.left_layout.addWidget(self.address_inputs["region"])
        self.left_layout.addWidget(QLabel("Город:"))
        self.left_layout.addWidget(self.address_inputs["city"])
        self.left_layout.addWidget(QLabel("Улица:"))
        self.left_layout.addWidget(self.address_inputs["street"])
        self.left_layout.addWidget(QLabel("Дом:"))
        self.left_layout.addWidget(self.address_inputs["home"])
        self.left_layout.addWidget(QLabel("Индекс:"))
        self.left_layout.addWidget(self.address_inputs["index"])
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        for btn in [self.add_btn, self.edit_btn, self.delete_btn]:
            StyleHelper.apply_button_style(btn)
        self.delete_btn.setStyleSheet("background-color: #ff4444; color: #fff;")
        self.add_btn.clicked.connect(self.add_driver)
        self.edit_btn.clicked.connect(self.edit_driver)
        self.delete_btn.clicked.connect(self.delete_driver)
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.left_layout.addLayout(self.btn_layout)
        self.left_layout.addStretch()
        load_photo(self.driver.photo, self.photo_label)

    def update_ui(self):
        self.driver = session.query(Driver).get(self.driver.driver_id)
        self.title_btn.setText(f"{self.driver.surname} {self.driver.name} {self.driver.middle_name or ''}")
        self.inputs["surname"].setText(str(self.driver.surname or ""))
        self.inputs["name"].setText(str(self.driver.name or ""))
        self.inputs["middle_name"].setText(str(self.driver.middle_name or ""))
        self.inputs["phone"].setText(str(self.driver.phone or ""))
        self.inputs["experience"].setText(str(self.driver.experience) if self.driver.experience is not None else "")
        self.inputs["series"].setText(str(self.driver.drivers_license_series or ""))
        self.inputs["number"].setText(str(self.driver.drivers_license_numbers or ""))
        
        address = session.query(Address).get(self.driver.address_id) if self.driver.address_id else Address()
        self.address_inputs["region"].setText(str(address.region or ""))
        self.address_inputs["city"].setText(str(address.city or ""))
        self.address_inputs["street"].setText(str(address.street or ""))
        self.address_inputs["home"].setText(str(address.home) if address.home is not None else "")
        self.address_inputs["index"].setText(str(address.index) if address.index is not None else "")
        
        load_photo(self.driver.photo, self.photo_label)

    def add_driver(self):
        dialog = AddDriverDialog()
        if dialog.exec():
            show_message("Успех", "Водитель успешно добавлен!")
            self.accept()

    def edit_driver(self):
        dialog = EditDriverDialog(self.driver)
        if dialog.exec():
            self.update_ui()
            show_message("Успех", "Водитель успешно отредактирован!")

    def delete_driver(self):
        if show_message("Подтверждение", f"Действительно ли удалить водителя {self.driver.surname} {self.driver.name}?", "question"):
            session.delete(self.driver)
            session.commit()
            show_message("Успех", "Водитель успешно удален!")
            self.accept()

# Диалог добавления водителя
class AddDriverDialog(BaseDialog):
    def __init__(self):
        super().__init__("Добавление водителя", size=(800, 800))
        self.setup_ui()

    def setup_ui(self):
        self.setup_layout("Новый водитель")
        self.inputs = {
            "surname": QLineEdit(),
            "name": QLineEdit(),
            "middle_name": QLineEdit(),
            "phone": QLineEdit(),
            "experience": QLineEdit(),
            "series": QLineEdit(),
            "number": QLineEdit()
        }
        self.address_inputs = {
            "region": QLineEdit(),
            "city": QLineEdit(),
            "street": QLineEdit(),
            "home": QLineEdit(),
            "index": QLineEdit()
        }
        for input_field in list(self.inputs.values()) + list(self.address_inputs.values()):
            StyleHelper.apply_widget_style(input_field)
        self.inputs["phone"].setMaxLength(12)
        self.inputs["experience"].setValidator(QIntValidator(0, 100, self))
        self.inputs["series"].setValidator(QIntValidator(0, 9999, self))
        self.inputs["series"].setMaxLength(4)
        self.inputs["number"].setValidator(QIntValidator(0, 999999, self))
        self.inputs["number"].setMaxLength(6)
        self.address_inputs["home"].setValidator(QIntValidator(0, 9999, self))
        self.address_inputs["index"].setValidator(QIntValidator(0, 999999, self))
        self.left_layout.addWidget(QLabel("Фамилия:"))
        self.left_layout.addWidget(self.inputs["surname"])
        self.left_layout.addWidget(QLabel("Имя:"))
        self.left_layout.addWidget(self.inputs["name"])
        self.left_layout.addWidget(QLabel("Отчество:"))
        self.left_layout.addWidget(self.inputs["middle_name"])
        self.left_layout.addWidget(QLabel("Телефон:"))
        self.left_layout.addWidget(self.inputs["phone"])
        self.left_layout.addWidget(QLabel("Стаж:"))
        self.left_layout.addWidget(self.inputs["experience"])
        self.left_layout.addWidget(QLabel("Серия ВУ:"))
        self.left_layout.addWidget(self.inputs["series"])
        self.left_layout.addWidget(QLabel("Номер ВУ:"))
        self.left_layout.addWidget(self.inputs["number"])
        self.left_layout.addWidget(QLabel("Регион:"))
        self.left_layout.addWidget(self.address_inputs["region"])
        self.left_layout.addWidget(QLabel("Город:"))
        self.left_layout.addWidget(self.address_inputs["city"])
        self.left_layout.addWidget(QLabel("Улица:"))
        self.left_layout.addWidget(self.address_inputs["street"])
        self.left_layout.addWidget(QLabel("Дом:"))
        self.left_layout.addWidget(self.address_inputs["home"])
        self.left_layout.addWidget(QLabel("Индекс:"))
        self.left_layout.addWidget(self.address_inputs["index"])
        self.photo_btn = QPushButton("Выбрать фото")
        StyleHelper.apply_button_style(self.photo_btn)
        self.photo_btn.clicked.connect(self.select_photo)
        self.left_layout.addWidget(self.photo_btn)
        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        StyleHelper.apply_button_style(self.save_btn)
        self.save_btn.clicked.connect(self.save_driver)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.save_btn)
        self.left_layout.addLayout(self.btn_layout)
        self.left_layout.addStretch()
        load_photo(None, self.photo_label)

    def select_photo(self):
        self.photo_data = select_photo(self, self.photo_label)

    def save_driver(self):
        required_fields = ["surname", "name", "phone", "series", "number"]
        if not all(self.inputs[field].text() for field in required_fields):
            show_message("Ошибка", "Заполните все обязательные поля!", "warning")
            return
        if len(self.inputs["phone"].text()) != 12:
            show_message("Ошибка", "Телефон должен содержать ровно 12 цифр!", "warning")
            return
        if len(self.inputs["series"].text()) != 4:
            show_message("Ошибка", "Серия ВУ должна содержать 4 цифры!", "warning")
            return
        if len(self.inputs["number"].text()) != 6:
            show_message("Ошибка", "Номер ВУ должен содержать 6 цифр!", "warning")
            return
        if not self.inputs["phone"].text().isdigit():
            show_message("Ошибка", "Телефон должен содержать только цифры!", "warning")
            return
        address_fields = {key: self.address_inputs[key].text() for key in self.address_inputs}
        if any(address_fields.values()):
            address = Address(
                region=address_fields["region"] or None,
                city=address_fields["city"] or None,
                street=address_fields["street"] or None,
                home=int(address_fields["home"]) if address_fields["home"] else None,
                index=int(address_fields["index"]) if address_fields["index"] else None
            )
            session.add(address)
            session.flush()
            address_id = address.address_id
        else:
            address_id = None
        driver = Driver(
            surname=self.inputs["surname"].text(),
            name=self.inputs["name"].text(),
            middle_name=self.inputs["middle_name"].text() or None,
            phone=self.inputs["phone"].text(),
            experience=int(self.inputs["experience"].text()) if self.inputs["experience"].text() else None,
            drivers_license_series=self.inputs["series"].text(),
            drivers_license_numbers=self.inputs["number"].text(),
            address_id=address_id,
            photo=self.photo_data if hasattr(self, "photo_data") else None
        )
        session.add(driver)
        session.commit()
        self.accept()

# Диалог редактирования водителя
class EditDriverDialog(BaseDialog):
    def __init__(self, driver):
        self.driver = driver
        super().__init__(f"Редактирование водителя: {driver.surname} {driver.name}", size=(800, 800))
        self.setup_ui()

    def setup_ui(self):
        self.setup_layout(f"{self.driver.surname} {self.driver.name} {self.driver.middle_name or ''}")
        self.inputs = {
            "surname": QLineEdit(str(self.driver.surname or "")),
            "name": QLineEdit(str(self.driver.name or "")),
            "middle_name": QLineEdit(str(self.driver.middle_name or "")),
            "phone": QLineEdit(str(self.driver.phone or "")),
            "experience": QLineEdit(str(self.driver.experience) if self.driver.experience is not None else ""),
            "series": QLineEdit(str(self.driver.drivers_license_series or "")),
            "number": QLineEdit(str(self.driver.drivers_license_numbers or ""))
        }
        address = session.query(Address).get(self.driver.address_id) if self.driver.address_id else Address()
        self.address_inputs = {
            "region": QLineEdit(str(address.region or "")),
            "city": QLineEdit(str(address.city or "")),
            "street": QLineEdit(str(address.street or "")),
            "home": QLineEdit(str(address.home) if address.home is not None else ""),
            "index": QLineEdit(str(address.index) if address.index is not None else "")
        }
        for input_field in list(self.inputs.values()) + list(self.address_inputs.values()):
            StyleHelper.apply_widget_style(input_field)
        self.inputs["phone"].setMaxLength(11)
        self.inputs["experience"].setValidator(QIntValidator(0, 100, self))
        self.inputs["series"].setValidator(QIntValidator(0, 9999, self))
        self.inputs["series"].setMaxLength(4)
        self.inputs["number"].setValidator(QIntValidator(0, 999999, self))
        self.inputs["number"].setMaxLength(6)
        self.address_inputs["home"].setValidator(QIntValidator(0, 9999, self))
        self.address_inputs["index"].setValidator(QIntValidator(0, 999999, self))
        self.left_layout.addWidget(QLabel("Фамилия:"))
        self.left_layout.addWidget(self.inputs["surname"])
        self.left_layout.addWidget(QLabel("Имя:"))
        self.left_layout.addWidget(self.inputs["name"])
        self.left_layout.addWidget(QLabel("Отчество:"))
        self.left_layout.addWidget(self.inputs["middle_name"])
        self.left_layout.addWidget(QLabel("Телефон:"))
        self.left_layout.addWidget(self.inputs["phone"])
        self.left_layout.addWidget(QLabel("Стаж:"))
        self.left_layout.addWidget(self.inputs["experience"])
        self.left_layout.addWidget(QLabel("Серия ВУ:"))
        self.left_layout.addWidget(self.inputs["series"])
        self.left_layout.addWidget(QLabel("Номер ВУ:"))
        self.left_layout.addWidget(self.inputs["number"])
        self.left_layout.addWidget(QLabel("Регион:"))
        self.left_layout.addWidget(self.address_inputs["region"])
        self.left_layout.addWidget(QLabel("Город:"))
        self.left_layout.addWidget(self.address_inputs["city"])
        self.left_layout.addWidget(QLabel("Улица:"))
        self.left_layout.addWidget(self.address_inputs["street"])
        self.left_layout.addWidget(QLabel("Дом:"))
        self.left_layout.addWidget(self.address_inputs["home"])
        self.left_layout.addWidget(QLabel("Индекс:"))
        self.left_layout.addWidget(self.address_inputs["index"])
        self.photo_btn = QPushButton("Заменить фото")
        StyleHelper.apply_button_style(self.photo_btn)
        self.photo_btn.clicked.connect(self.select_photo)
        self.left_layout.addWidget(self.photo_btn)
        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        StyleHelper.apply_button_style(self.save_btn)
        self.save_btn.clicked.connect(self.save_driver)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.save_btn)
        self.left_layout.addLayout(self.btn_layout)
        self.left_layout.addStretch()
        load_photo(self.driver.photo, self.photo_label)

    def select_photo(self):
        self.photo_data = select_photo(self, self.photo_label)

    def save_driver(self):
        required_fields = ["surname", "name", "phone", "series", "number"]
        if not all(self.inputs[field].text() for field in required_fields):
            show_message("Ошибка", "Заполните все обязательные поля!", "warning")
            return
        if len(self.inputs["phone"].text()) != 11:
            show_message("Ошибка", "Телефон должен содержать ровно 11 цифр!", "warning")
            return
        if len(self.inputs["series"].text()) != 4:
            show_message("Ошибка", "Серия ВУ должна содержать 4 цифры!", "warning")
            return
        if len(self.inputs["number"].text()) != 6:
            show_message("Ошибка", "Номер ВУ должен содержать 6 цифр!", "warning")
            return
        if not self.inputs["phone"].text().isdigit():
            show_message("Ошибка", "Телефон должен содержать только цифры!", "warning")
            return
        address_fields = {key: self.address_inputs[key].text() for key in self.address_inputs}
        if any(address_fields.values()):
            if not self.driver.address_id:
                address = Address()
                session.add(address)
                session.flush()
                self.driver.address_id = address.address_id
            else:
                address = session.query(Address).get(self.driver.address_id)
            address.region = address_fields["region"] or None
            address.city = address_fields["city"] or None
            address.street = address_fields["street"] or None
            address.home = int(address_fields["home"]) if address_fields["home"] else None
            address.index = int(address_fields["index"]) if address_fields["index"] else None
        else:
            self.driver.address_id = None
        self.driver.surname = self.inputs["surname"].text()
        self.driver.name = self.inputs["name"].text()
        self.driver.middle_name = self.inputs["middle_name"].text() or None
        self.driver.phone = self.inputs["phone"].text()
        self.driver.experience = int(self.inputs["experience"].text()) if self.inputs["experience"].text() else None
        self.driver.drivers_license_series = self.inputs["series"].text()
        self.driver.drivers_license_numbers = self.inputs["number"].text()
        if hasattr(self, "photo_data"):
            self.driver.photo = self.photo_data
        session.commit()
        self.accept()

# Диалог ТО и расходов
class CarServiceExpensesDialog(QDialog):
    def __init__(self, car):
        super().__init__()
        self.car = car
        self.setWindowTitle(f"ТО и Расходы: {car.mark} {car.model}")
        self.setWindowIcon(QIcon("car_icon.png"))
        self.setMinimumSize(700, 600)

        self.main_layout = QVBoxLayout()
        self.car_title = QPushButton(f"{car.mark} {car.model}")
        StyleHelper.apply_title_style(self.car_title)
        self.main_layout.addWidget(self.car_title, alignment=Qt.AlignCenter)

        self.content_layout = QVBoxLayout()

        self.service_label = QLabel("Техническое обслуживание:")
        StyleHelper.apply_widget_style(self.service_label)
        self.content_layout.addWidget(self.service_label)
        
        self.service_table = QTableWidget()
        self.service_table.setColumnCount(5)
        self.service_table.setHorizontalHeaderLabels(["Дата ТО", "Тип работ", "Следующее ТО", "Пробег на момент ТО", "Заключение"])
        StyleHelper.apply_widget_style(self.service_table)
        self.load_services()
        self.content_layout.addWidget(self.service_table)

        self.service_btn_layout = QHBoxLayout()
        self.add_service_btn = QPushButton("Добавить")
        self.edit_service_btn = QPushButton("Редактировать")
        StyleHelper.apply_button_style(self.add_service_btn)
        StyleHelper.apply_button_style(self.edit_service_btn)
        self.add_service_btn.clicked.connect(self.add_service)
        self.edit_service_btn.clicked.connect(self.edit_service)
        self.service_btn_layout.addWidget(self.add_service_btn)
        self.service_btn_layout.addWidget(self.edit_service_btn)
        self.service_btn_layout.addStretch()
        self.content_layout.addLayout(self.service_btn_layout)

        self.expenses_label = QLabel("Расходы:")
        StyleHelper.apply_widget_style(self.expenses_label)
        self.content_layout.addWidget(self.expenses_label)
        
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(3)
        self.expenses_table.setHorizontalHeaderLabels(["Тип расхода", "Сумма", "Дата"])
        StyleHelper.apply_widget_style(self.expenses_table)
        self.load_expenses()
        self.content_layout.addWidget(self.expenses_table)

        self.expenses_btn_layout = QHBoxLayout()
        self.add_expenses_btn = QPushButton("Добавить")
        self.edit_expenses_btn = QPushButton("Редактировать")
        StyleHelper.apply_button_style(self.add_expenses_btn)
        StyleHelper.apply_button_style(self.edit_expenses_btn)
        self.add_expenses_btn.clicked.connect(self.add_expenses)
        self.edit_expenses_btn.clicked.connect(self.edit_expenses)
        self.expenses_btn_layout.addWidget(self.add_expenses_btn)
        self.expenses_btn_layout.addWidget(self.edit_expenses_btn)
        self.expenses_btn_layout.addStretch()
        self.content_layout.addLayout(self.expenses_btn_layout)

        self.report_btn_layout = QHBoxLayout()
        self.car_report_btn = QPushButton("Отчёт по автомобилю")
        self.expenses_report_btn = QPushButton("Отчёт по расходам")
        self.service_schedule_btn = QPushButton("График ТО")
        for btn in [self.car_report_btn, self.expenses_report_btn, self.service_schedule_btn]:
            StyleHelper.apply_button_style(btn)
        self.car_report_btn.clicked.connect(self.generate_car_report)
        self.expenses_report_btn.clicked.connect(self.generate_expenses_report)
        self.service_schedule_btn.clicked.connect(self.generate_service_schedule)
        self.report_btn_layout.addWidget(self.car_report_btn)
        self.report_btn_layout.addWidget(self.expenses_report_btn)
        self.report_btn_layout.addWidget(self.service_schedule_btn)
        self.content_layout.addLayout(self.report_btn_layout)

        self.close_btn = QPushButton("Закрыть")
        StyleHelper.apply_button_style(self.close_btn)
        self.close_btn.clicked.connect(self.accept)
        self.content_layout.addWidget(self.close_btn, alignment=Qt.AlignCenter)
        self.main_layout.addLayout(self.content_layout)
        self.setLayout(self.main_layout)

        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        except Exception as e:
            show_message("Ошибка", f"Не удалось загрузить шрифт DejaVuSans: {str(e)}", "warning")

    def load_services(self):
        services = session.query(ServiceCar).filter_by(car_id=self.car.car_id).all()
        self.service_table.setRowCount(len(services))
        for row, service in enumerate(services):
            self.service_table.setItem(row, 0, QTableWidgetItem(service.date_service.strftime('%Y-%m-%d') if service.date_service else ""))
            self.service_table.setItem(row, 1, QTableWidgetItem(service.type_work.type if service.type_work else ""))
            self.service_table.setItem(row, 2, QTableWidgetItem(service.next_date.strftime('%Y-%m-%d') if service.next_date else ""))
            self.service_table.setItem(row, 3, QTableWidgetItem(str(service.mileage_at_service) if service.mileage_at_service is not None else ""))
            self.service_table.setItem(row, 4, QTableWidgetItem(service.conclusion or ""))
        self.service_table.resizeColumnsToContents()

    def load_expenses(self):
        expenses = session.query(ExpensesCar).filter_by(car_id=self.car.car_id).all()
        self.expenses_table.setRowCount(len(expenses))
        for row, expense in enumerate(expenses):
            self.expenses_table.setItem(row, 0, QTableWidgetItem(expense.type_expenses.type_expenses if expense.type_expenses else ""))
            self.expenses_table.setItem(row, 1, QTableWidgetItem(str(expense.sum) if expense.sum is not None else "0.0"))
            self.expenses_table.setItem(row, 2, QTableWidgetItem(expense.date_expenses.strftime('%Y-%m-%d') if expense.date_expenses else ""))
        self.expenses_table.resizeColumnsToContents()

    # Обновление пробега автомобиля относительно крайней записи в ТО
    def update_car_mileage(self):
        latest_service = session.query(ServiceCar).filter_by(car_id=self.car.car_id)\
            .order_by(ServiceCar.date_service.desc()).first()
        if latest_service and latest_service.mileage_at_service is not None:
            self.car.mileage = latest_service.mileage_at_service
            session.commit()

    def add_service(self):
        dialog = AddServiceCarDialog(self.car)
        if dialog.exec():
            new_service = dialog.get_service_data()
            if new_service:
                session.add(new_service)
                session.commit()
                self.load_services()
                self.update_car_mileage()
                if hasattr(self.parent(), 'card'):
                    self.parent().card.update_card()

    def edit_service(self):
        selected_row = self.service_table.currentRow()
        if selected_row >= 0:
            services = session.query(ServiceCar).filter_by(car_id=self.car.car_id).all()
            if selected_row < len(services):
                dialog = EditServiceCarDialog(services[selected_row])
                if dialog.exec():
                    if dialog.is_deleted:
                        session.delete(services[selected_row])
                    session.commit()
                    self.load_services()
                    self.update_car_mileage()
                    if hasattr(self.parent(), 'card'):
                        self.parent().card.update_card()

    def add_expenses(self):
        dialog = AddExpensesCarDialog(self.car)
        if dialog.exec():
            new_expense = dialog.get_expense_data()
            if new_expense:
                session.add(new_expense)
                session.commit()
                self.load_expenses()

    def edit_expenses(self):
        selected_row = self.expenses_table.currentRow()
        if selected_row >= 0:
            expenses = session.query(ExpensesCar).filter_by(car_id=self.car.car_id).all()
            if selected_row < len(expenses):
                dialog = EditExpensesCarDialog(expenses[selected_row])
                if dialog.exec():
                    if dialog.is_deleted:
                        session.delete(expenses[selected_row])
                    session.commit()
                    self.load_expenses()
                    
    # Отчет об автомобиле
    def generate_car_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчёт по автомобилю", f"Отчёт_{self.car.mark}_{self.car.model}.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title_style.fontName = "DejaVuSans"
        normal_style = styles["Normal"]
        normal_style.fontName = "DejaVuSans"
        normal_style.fontSize = 12
        elements = []

        elements.append(Paragraph(f"Отчёт по автомобилю: {self.car.mark} {self.car.model}", title_style))
        elements.append(Spacer(1, 12))

        driver = self.car.driver
        data = [
            f"Марка: {self.car.mark}",
            f"Модель: {self.car.model}",
            f"Номер: {self.car.number}",
            f"Пробег: {self.car.mileage} км",
            f"Год: {self.car.year}",
            f"Статус: {self.car.status.status}",
            f"Водитель: {driver.surname} {driver.name} {driver.middle_name or ''}" if driver else "Водитель: Не назначен",
        ]
        for line in data:
            elements.append(Paragraph(line, normal_style))
            elements.append(Spacer(1, 6))

        doc.build(elements)
        show_message("Успех", f"Отчёт сохранён по пути: {file_path}")

    # Отчет по затратам на автомобиль
    def generate_expenses_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчёт по расходам", f"Расходы_{self.car.mark}_{self.car.model}.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title_style.fontName = "DejaVuSans"
        normal_style = styles["Normal"]
        normal_style.fontName = "DejaVuSans"
        normal_style.fontSize = 10
        elements = []

        elements.append(Paragraph(f"Отчёт по расходам на автомобиль: {self.car.mark} {self.car.model}", title_style))
        elements.append(Spacer(1, 12))

        expenses = session.query(ExpensesCar).filter_by(car_id=self.car.car_id).all()
        if not expenses:
            elements.append(Paragraph("Расходы отсутствуют.", normal_style))
        else:
            data = [["Тип расхода", "Сумма", "Дата"]]
            for expense in expenses:
                data.append([
                    expense.type_expenses.type_expenses if expense.type_expenses else "",
                    str(expense.sum) if expense.sum is not None else "0.0",
                    expense.date_expenses.strftime('%Y-%m-%d') if expense.date_expenses else ""
                ])
            table = Table(data, colWidths=[200, 100, 100])
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'DejaVuSans'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ]))
            elements.append(table)

        doc.build(elements)
        show_message("Успех", f"Отчёт сохранён по пути: {file_path}")

    # График ТО
    def generate_service_schedule(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить график ТО", f"График_ТО_{self.car.mark}_{self.car.model}.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title_style.fontName = "DejaVuSans"
        normal_style = styles["Normal"]
        normal_style.fontName = "DejaVuSans"
        normal_style.fontSize = 10
        elements = []

        elements.append(Paragraph(f"График ТО для автомобиля: {self.car.mark} {self.car.model}", title_style))
        elements.append(Spacer(1, 12))

        services = session.query(ServiceCar).filter_by(car_id=self.car.car_id).order_by(ServiceCar.date_service).all()
        if not services:
            elements.append(Paragraph("ТО отсутствуют.", normal_style))
        else:
            drawing = Drawing(500, 400)
            x_base = 50
            y_start = 350
            y_end = 50
            drawing.add(Line(x_base, y_start, x_base, y_end))

            valid_services = [s for s in services if s.date_service is not None]
            if not valid_services:
                elements.append(Paragraph("Нет данных о датах ТО.", normal_style))
            else:
                earliest_date = min(s.date_service for s in valid_services).toordinal()
                latest_date = max(s.next_date.toordinal() if s.next_date else s.date_service.toordinal() for s in valid_services)
                date_range = latest_date - earliest_date if latest_date > earliest_date else 1

                min_text_spacing = 25
                last_y_position = y_start
                service_dates = {s.date_service.strftime('%Y-%m-%d') for s in valid_services}

                for service in valid_services:
                    date_pos = y_start - ((service.date_service.toordinal() - earliest_date) / date_range) * (y_start - y_end)
                    next_date_pos = y_start - ((service.next_date.toordinal() - earliest_date) / date_range) * (y_start - y_end) if service.next_date else None

                    drawing.add(Line(x_base, date_pos, x_base + 20, date_pos))
                    text_y = min(date_pos, last_y_position - min_text_spacing)
                    if text_y < y_end:
                        text_y = y_end
                    label = f"{service.date_service.strftime('%Y-%m-%d')} ({service.type_work.type if service.type_work else 'Не указано'})"
                    drawing.add(String(x_base + 25, text_y - 5, label, fontName="DejaVuSans", fontSize=8))
                    drawing.add(String(x_base + 25, text_y - 15, f"Пробег: {service.mileage_at_service or 0}, {service.conclusion or ''}", fontName="DejaVuSans", fontSize=8))
                    last_y_position = text_y - 15

                    if service.next_date and service.next_date.strftime('%Y-%m-%d') not in service_dates:
                        drawing.add(Line(x_base, next_date_pos, x_base + 10, next_date_pos, strokeDashArray=[4, 2]))
                        next_text_y = min(next_date_pos, last_y_position - min_text_spacing)
                        if next_text_y < y_end:
                            next_text_y = y_end
                        drawing.add(String(x_base + 15, next_text_y - 5, f"След. ТО: {service.next_date.strftime('%Y-%m-%d')}", fontName="DejaVuSans", fontSize=8))
                        last_y_position = next_text_y - 5

                elements.append(drawing)

        doc.build(elements)
        show_message("Успех", f"График сохранён по пути: {file_path}")

# Диалог добавления ТО
class AddServiceCarDialog(QDialog):
    def __init__(self, car):
        super().__init__()
        self.car = car
        self.setWindowTitle("Добавление ТО")
        self.setMinimumSize(400, 450)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.layout.addWidget(QLabel("Дата ТО:"))
        self.layout.addWidget(self.date_input)

        self.type_work_combo = QComboBox()
        for type_work in session.query(TypeWork).all():
            self.type_work_combo.addItem(type_work.type, type_work.type_work_id)
        self.layout.addWidget(QLabel("Тип работ:"))
        self.layout.addWidget(self.type_work_combo)

        self.next_date_input = QDateEdit()
        self.next_date_input.setCalendarPopup(True)
        self.next_date_input.setDate(QDate.currentDate().addMonths(6))
        self.layout.addWidget(QLabel("Следующее ТО:"))
        self.layout.addWidget(self.next_date_input)

        self.mileage_input = QLineEdit(str(self.car.mileage) if self.car.mileage is not None else "0")
        self.mileage_input.setValidator(QIntValidator(0, 999999, self))
        self.layout.addWidget(QLabel("Пробег на момент ТО:"))
        self.layout.addWidget(self.mileage_input)

        self.conclusion_input = QLineEdit()
        self.layout.addWidget(QLabel("Заключение:"))
        self.layout.addWidget(self.conclusion_input)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        StyleHelper.apply_button_style(self.save_btn)
        StyleHelper.apply_button_style(self.cancel_btn)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)

    def get_service_data(self):
        if not self.mileage_input.text():
            show_message("Ошибка", "Введите пробег на момент ТО!", "warning")
            return None
        service = ServiceCar(
            car_id=self.car.car_id,
            mileage_at_service=int(self.mileage_input.text()),
            type_work_id=self.type_work_combo.currentData(),
            date_service=self.date_input.date().toPython(),
            next_date=self.next_date_input.date().toPython(),
            conclusion=self.conclusion_input.text() or None
        )
        return service

# Диалог редактирования ТО
class EditServiceCarDialog(QDialog):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.is_deleted = False
        self.setWindowTitle("Редактирование ТО")
        self.setMinimumSize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.fromString(self.service.date_service.strftime('%Y-%m-%d'), 'yyyy-MM-dd') if self.service.date_service else QDate.currentDate())
        self.layout.addWidget(QLabel("Дата ТО:"))
        self.layout.addWidget(self.date_input)

        self.type_work_combo = QComboBox()
        for type_work in session.query(TypeWork).all():
            self.type_work_combo.addItem(type_work.type, type_work.type_work_id)
        self.type_work_combo.setCurrentIndex(self.type_work_combo.findData(self.service.type_work_id))
        self.layout.addWidget(QLabel("Тип работ:"))
        self.layout.addWidget(self.type_work_combo)

        self.next_date_input = QDateEdit()
        self.next_date_input.setCalendarPopup(True)
        self.next_date_input.setDate(QDate.fromString(self.service.next_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd') if self.service.next_date else QDate.currentDate().addMonths(6))
        self.layout.addWidget(QLabel("Следующее ТО:"))
        self.layout.addWidget(self.next_date_input)

        self.mileage_input = QLineEdit(str(self.service.mileage_at_service) if self.service.mileage_at_service is not None else "0")
        self.mileage_input.setValidator(QIntValidator(0, 999999, self))
        self.layout.addWidget(QLabel("Пробег на момент ТО:"))
        self.layout.addWidget(self.mileage_input)

        self.conclusion_input = QLineEdit(self.service.conclusion or "")
        self.layout.addWidget(QLabel("Заключение:"))
        self.layout.addWidget(self.conclusion_input)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.delete_btn = QPushButton("Удалить")
        self.cancel_btn = QPushButton("Отмена")
        StyleHelper.apply_button_style(self.save_btn)
        StyleHelper.apply_button_style(self.delete_btn, color="#ff4444", extra="color: #fff;")
        StyleHelper.apply_button_style(self.cancel_btn)
        self.save_btn.clicked.connect(self.save_service)
        self.delete_btn.clicked.connect(self.delete_service)
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)

    def save_service(self):
        if not self.mileage_input.text():
            show_message("Ошибка", "Введите пробег на момент ТО!", "warning")
            return
        self.service.mileage_at_service = int(self.mileage_input.text())
        self.service.type_work_id = self.type_work_combo.currentData()
        self.service.date_service = self.date_input.date().toPython()
        self.service.next_date = self.next_date_input.date().toPython()
        self.service.conclusion = self.conclusion_input.text() or None
        session.commit()
        self.accept()

    def delete_service(self):
        self.is_deleted = True
        self.accept()

# Диалог добавления расходов
class AddExpensesCarDialog(QDialog):
    def __init__(self, car):
        super().__init__()
        self.car = car
        self.setWindowTitle("Добавление расходов")
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.type_expenses_combo = QComboBox()
        for type_expense in session.query(TypeExpenses).all():
            self.type_expenses_combo.addItem(type_expense.type_expenses, type_expense.type_expenses_id)
        self.layout.addWidget(QLabel("Тип расхода:"))
        self.layout.addWidget(self.type_expenses_combo)

        self.sum_input = QLineEdit()
        self.sum_input.setValidator(QDoubleValidator(0.0, 9999999.99, 2, self))
        self.layout.addWidget(QLabel("Сумма:"))
        self.layout.addWidget(self.sum_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.layout.addWidget(QLabel("Дата:"))
        self.layout.addWidget(self.date_input)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        StyleHelper.apply_button_style(self.save_btn)
        StyleHelper.apply_button_style(self.cancel_btn)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)

    def get_expense_data(self):
        if not self.sum_input.text():
            show_message("Ошибка", "Введите сумму!", "warning")
            return None
        expense = ExpensesCar(
            car_id=self.car.car_id,
            type_expenses_id=self.type_expenses_combo.currentData(),
            sum=float(self.sum_input.text()),
            date_expenses=self.date_input.date().toPython()
        )
        return expense

# Диалог редактирования расходов
class EditExpensesCarDialog(QDialog):
    def __init__(self, expense):
        super().__init__()
        self.expense = expense
        self.is_deleted = False
        self.setWindowTitle("Редактирование расходов")
        self.setMinimumSize(400, 350)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.type_expenses_combo = QComboBox()
        for type_expense in session.query(TypeExpenses).all():
            self.type_expenses_combo.addItem(type_expense.type_expenses, type_expense.type_expenses_id)
        self.type_expenses_combo.setCurrentIndex(self.type_expenses_combo.findData(self.expense.type_expenses_id))
        self.layout.addWidget(QLabel("Тип расхода:"))
        self.layout.addWidget(self.type_expenses_combo)

        self.sum_input = QLineEdit(str(self.expense.sum) if self.expense.sum is not None else "0.0")
        self.sum_input.setValidator(QDoubleValidator(0.0, 9999999.99, 2, self))
        self.layout.addWidget(QLabel("Сумма:"))
        self.layout.addWidget(self.sum_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.fromString(self.expense.date_expenses.strftime('%Y-%m-%d'), 'yyyy-MM-dd') if self.expense.date_expenses else QDate.currentDate())
        self.layout.addWidget(QLabel("Дата:"))
        self.layout.addWidget(self.date_input)

        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.delete_btn = QPushButton("Удалить")
        self.cancel_btn = QPushButton("Отмена")
        StyleHelper.apply_button_style(self.save_btn)
        StyleHelper.apply_button_style(self.delete_btn, color="#ff4444", extra="color: #fff;")
        StyleHelper.apply_button_style(self.cancel_btn)
        self.save_btn.clicked.connect(self.save_expense)
        self.delete_btn.clicked.connect(self.delete_expense)
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)

    def save_expense(self):
        if not self.sum_input.text():
            show_message("Ошибка", "Введите сумму!", "warning")
            return
        try:
            self.expense.type_expenses_id = self.type_expenses_combo.currentData()
            self.expense.sum = float(self.sum_input.text())
            self.expense.date_expenses = self.date_input.date().toPython()
            session.commit()
            self.accept()
        except ValueError:
            show_message("Ошибка", "Сумма должна быть числом!", "warning")

    def delete_expense(self):
        self.is_deleted = True
        self.accept()

# Диалог архива автомобилей
class ArchiveDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Архив автомобилей")
        self.setWindowIcon(QIcon("car_icon.png"))
        self.setMinimumSize(400, 400)
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.header_label = QPushButton("Архив автомобилей")
        StyleHelper.apply_title_style(self.header_label)
        self.main_layout.addWidget(self.header_label, alignment=Qt.AlignCenter)

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        StyleHelper.apply_widget_style(self.search_input)
        self.search_input.setPlaceholderText("Поиск по номеру или названию")
        self.search_btn = QPushButton("Найти")
        StyleHelper.apply_button_style(self.search_btn, extra="min-width: 100px;")
        self.search_btn.clicked.connect(self.search_in_archive)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_btn)
        self.main_layout.addLayout(self.search_layout)

        self.archive_list = QListWidget()
        StyleHelper.apply_widget_style(self.archive_list, "border: 1px solid #ffd700; border-radius: 5px;")
        self.archived_cars = session.query(Car).filter_by(is_archived=True).all()
        self.load_archive_list(self.archived_cars)
        self.archive_list.itemDoubleClicked.connect(self.show_car_details)
        self.main_layout.addWidget(self.archive_list)

        self.btn_layout = QHBoxLayout()
        self.restore_btn = QPushButton("Восстановить")
        self.close_btn = QPushButton("Закрыть")
        StyleHelper.apply_button_style(self.restore_btn)
        StyleHelper.apply_button_style(self.close_btn)
        self.restore_btn.clicked.connect(self.restore_car)
        self.close_btn.clicked.connect(self.accept)
        self.btn_layout.addWidget(self.restore_btn)
        self.btn_layout.addWidget(self.close_btn)
        self.main_layout.addLayout(self.btn_layout)
        self.setLayout(self.main_layout)

    def load_archive_list(self, cars):
        self.archive_list.clear()
        for car in cars:
            item = QListWidgetItem(f"{car.mark} {car.model} ({car.number})")
            item.setData(Qt.UserRole, car.car_id)
            self.archive_list.addItem(item)

    def show_car_details(self, item):
        car_id = item.data(Qt.UserRole)
        car = session.query(Car).get(car_id)
        dialog = CarDetailsDialog(car)
        dialog.exec()

    def restore_car(self):
        current_item = self.archive_list.currentItem()
        if current_item:
            car_id = current_item.data(Qt.UserRole)
            car = session.query(Car).get(car_id)
            car.is_archived = False
            session.commit()
            self.archived_cars = session.query(Car).filter_by(is_archived=True).all()
            self.load_archive_list(self.archived_cars)
            self.parent.cars = session.query(Car).filter_by(is_archived=False).all()
            self.parent.load_current_car()

    def search_in_archive(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.load_archive_list(self.archived_cars)
            return
        filtered_cars = [car for car in self.archived_cars if query in car.number.lower() or query in f"{car.mark} {car.model}".lower()]
        self.load_archive_list(filtered_cars)
        if not filtered_cars:
            show_message("Результат", "Автомобиль не найден в архиве.")

# Диалог деталей автомобиля в архиве
class CarDetailsDialog(BaseDialog):
    def __init__(self, car):
        self.car = car
        super().__init__(f"Детали: {car.mark} {car.model}", size=(700, 450))
        self.setup_ui()

    def setup_ui(self):
        self.setup_layout(f"{self.car.mark} {self.car.model}")
        self.inputs = {
            "mark": QLineEdit(str(self.car.mark or "")),
            "model": QLineEdit(str(self.car.model or "")),
            "number": QLineEdit(str(self.car.number or "")),
            "mileage": QLineEdit(str(self.car.mileage) if self.car.mileage is not None else "0"),
            "year": QLineEdit(str(self.car.year) if self.car.year is not None else "")
        }
        for input_field in self.inputs.values():
            StyleHelper.apply_widget_style(input_field)
            input_field.setReadOnly(True)

        self.left_layout.addWidget(QLabel("Марка:"))
        self.left_layout.addWidget(self.inputs["mark"])
        self.left_layout.addWidget(QLabel("Модель:"))
        self.left_layout.addWidget(self.inputs["model"])
        self.left_layout.addWidget(QLabel("Номер:"))
        self.left_layout.addWidget(self.inputs["number"])
        self.left_layout.addWidget(QLabel("Пробег:"))
        self.left_layout.addWidget(self.inputs["mileage"])
        self.left_layout.addWidget(QLabel("Год:"))
        self.left_layout.addWidget(self.inputs["year"])

        self.status_combo = QComboBox()
        StyleHelper.apply_widget_style(self.status_combo)
        for status in session.query(Status).all():
            self.status_combo.addItem(status.status, status.status_id)
        self.status_combo.setCurrentIndex(self.status_combo.findData(self.car.status_id))
        self.status_combo.setEnabled(False)
        self.left_layout.addWidget(QLabel("Статус:"))
        self.left_layout.addWidget(self.status_combo)

        self.driver_combo = QComboBox()
        StyleHelper.apply_widget_style(self.driver_combo)
        self.driver_combo.addItem("Без водителя", None)
        for driver in session.query(Driver).all():
            self.driver_combo.addItem(f"{driver.surname} {driver.name}", driver.driver_id)
        self.driver_combo.setCurrentIndex(self.driver_combo.findData(self.car.driver_id))
        self.driver_combo.setEnabled(False)
        self.left_layout.addWidget(QLabel("Водитель:"))
        self.left_layout.addWidget(self.driver_combo)

        self.left_layout.addStretch()
        load_photo(self.car.photo, self.photo_label)