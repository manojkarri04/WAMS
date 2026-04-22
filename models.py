from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ==========================================
# BASE USER CLASS
# ==========================================
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    _password = Column('password', String, nullable=False) 
    role = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }

# ==========================================
# CHILD CLASSES (The 4 Roles)
# ==========================================
class Admin(User):
    __tablename__ = 'admins'
    admin_id = Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True)
    name = Column(String, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'admin'}

class Dealer(User):
    __tablename__ = 'dealers'
    dealer_id = Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True)

    # ---> ADD THIS MISSING LINE <---
    orders = relationship("Order", back_populates="dealer")

    __mapper_args__ = {'polymorphic_identity': 'dealer'}

class Supplier(User):
    __tablename__ = 'suppliers'
    supplier_id = Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'supplier'}

class ManagementAuthority(User):
    __tablename__ = 'management_authorities'
    management_id = Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'management'}

# ==========================================
# INVENTORY & ORDER CLASSES
# ==========================================
class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String, nullable=False)
    category = Column(String)
    unit_price = Column(Float)
    stock_level = Column(Integer, default=0) 

    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    order_date = Column(Date)
    status = Column(String)
    quantity = Column(Integer, nullable=False)

    dealer_id = Column(Integer, ForeignKey('dealers.user_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))

    dealer = relationship("Dealer", back_populates="orders")
    product = relationship("Product", back_populates="orders")


# Add this above or replace the previous Quotation model in models.py

class MaterialRequest(Base):
    __tablename__ = 'material_requests'
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    material_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="Open") # Can be "Open" or "Closed"
    
    quotations = relationship("Quotation", back_populates="material_request")

class Quotation(Base):
    __tablename__ = 'quotations'
    quotation_id = Column(Integer, primary_key=True, autoincrement=True)
    quoted_price = Column(Float, nullable=False) # 
    lead_time_days = Column(Integer, nullable=False) # Supplier enters lead time [cite: 136]
    
    supplier_id = Column(Integer, ForeignKey('suppliers.user_id'))
    request_id = Column(Integer, ForeignKey('material_requests.request_id')) # Links quote to request 
    
    material_request = relationship("MaterialRequest", back_populates="quotations")


class ProductionBatch(Base):
    __tablename__ = 'production_batches'
    batch_id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer) # [cite: 355]
    status = Column(String) # [cite: 355]
    end_date = Column(Date) # [cite: 355]
    
    product_id = Column(Integer, ForeignKey('products.product_id'))

class Invoice(Base):
    __tablename__ = 'invoices'
    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float) # [cite: 359]
    gst = Column(Float) # [cite: 359]
    invoice_date = Column(Date) # [cite: 359]
    
    order_id = Column(Integer, ForeignKey('orders.order_id'))


