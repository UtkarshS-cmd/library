# models.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey,DateTime
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from sqlalchemy import select, func as sqlfunc
BASE_URL = os.getenv(
 'BASE_URL',
 'postgresql://postgres:141205@localhost:5432/restaurant')
engine = create_engine(
 BASE_URL,
 echo=True, # prints every SQL statement
 pool_size=5, # keep 5 connections open in pool
 max_overflow=10, # allow extra connections if needed
 )
class Base(DeclarativeBase): pass
class Restaurant(Base):
 __tablename__ = 'restaurants'
 restaurant_id = Column(Integer, primary_key=True)
 name = Column(String(150), nullable=False)
 city = Column(String(80), nullable=False)
 cuisine_type = Column(String(50))
 rating = Column(Numeric(2,1))
 is_active = Column(Boolean, default=True)
 orders = relationship('Order', back_populates='restaurant')
 menu_items = relationship('MenuItem', back_populates='restaurant',
 cascade='all, delete-orphan')
class Customer(Base):
 __tablename__ = 'customers'
 customer_id = Column(Integer, primary_key=True)
 full_name = Column(String(100), nullable=False)
 phone = Column(String(15), unique=True, nullable=False)
 city = Column(String(80))
 joined_at = Column(DateTime, server_default=func.now())
 orders = relationship('Order', back_populates='customer')
class Order(Base):
 __tablename__ = 'orders'
 order_id = Column(Integer, primary_key=True)
 customer_id = Column(Integer, ForeignKey('customers.customer_id'),
nullable=False)
 restaurant_id = Column(Integer, ForeignKey('restaurants.restaurant_id'),
nullable=False)
 order_date = Column(DateTime, server_default=func.now())
 status = Column(String(20), default='placed')
 total_amount = Column(Numeric(10,2))
 customer = relationship('Customer', back_populates='orders')
 restaurant = relationship('Restaurant', back_populates='orders')
 order_items = relationship('OrderItem', back_populates='order',
 cascade='all, delete-orphan')

 with SessionLocal() as session:
 r = Restaurant(name='Paradise Biryani', city='Hyderabad',
 cuisine_type='Hyderabadi', rating=4.7)
 session.add(r)
 session.commit()
 session.refresh(r)