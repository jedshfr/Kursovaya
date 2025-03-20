from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, LargeBinary, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine("postgresql://postgres:123@localhost:5432/kurs", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

class Address(Base):
    __tablename__ = 'address'
    address_id = Column(Integer, primary_key=True)
    region = Column(String(100))
    city = Column(String(100))
    street = Column(String(100))
    home = Column(Integer)
    index = Column(Integer)

class Driver(Base):
    __tablename__ = 'driver'
    driver_id = Column(Integer, primary_key=True)
    surname = Column(String(50))
    name = Column(String(50))
    middle_name = Column(String(50))
    phone = Column(String(12))
    experience = Column(Integer)
    drivers_license_series = Column(Integer)
    drivers_license_numbers = Column(Integer)
    address_id = Column(Integer, ForeignKey('address.address_id'))
    photo = Column(LargeBinary)

class Status(Base):
    __tablename__ = 'status'
    status_id = Column(Integer, primary_key=True)
    status = Column(String(50))

class TypeWork(Base):
    __tablename__ = 'type_work'
    type_work_id = Column(Integer, primary_key=True)
    type = Column(String(200))

class TypeExpenses(Base):
    __tablename__ = 'type_expenses'
    type_expenses_id = Column(Integer, primary_key=True)
    type_expenses = Column(String(200))

class ServiceCar(Base):
    __tablename__ = 'service_car'
    service_car_id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey('car.car_id'))
    mileage_at_service = Column(Integer)
    type_work_id = Column(Integer, ForeignKey('type_work.type_work_id'))
    date_service = Column(Date)
    next_date = Column(Date)
    conclusion = Column(String(500))
    car = relationship("Car", back_populates="services")
    type_work = relationship("TypeWork")

class ExpensesCar(Base):
    __tablename__ = 'expenses_car'
    expenses_car_id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey('car.car_id'))
    type_expenses_id = Column(Integer, ForeignKey('type_expenses.type_expenses_id'))
    sum = Column(Float) 
    date_expenses = Column(Date)
    car = relationship("Car", back_populates="expenses")
    type_expenses = relationship("TypeExpenses")

class Car(Base):
    __tablename__ = 'car'
    car_id = Column(Integer, primary_key=True)
    mark = Column(String(50))
    model = Column(String(50))
    number = Column(String(9))
    mileage = Column(Integer)
    year = Column(Integer)
    photo = Column(LargeBinary)
    status_id = Column(Integer, ForeignKey('status.status_id'))
    driver_id = Column(Integer, ForeignKey('driver.driver_id'), nullable=True)
    is_archived = Column(Boolean, default=False)
    driver = relationship("Driver")
    status = relationship("Status")
    services = relationship("ServiceCar", back_populates="car") 
    expenses = relationship("ExpensesCar", back_populates="car")  