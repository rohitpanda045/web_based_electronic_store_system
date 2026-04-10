from extensions import db
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'ADMIN'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class User(db.Model):
    __tablename__ = 'USER'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')

class Product(db.Model):
    __tablename__ = 'PRODUCT'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_name = db.Column(db.String(150), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0.00)
    stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    features = db.Column(db.Text)
    warranty = db.Column(db.String(100))
    category = db.Column(db.String(100))
    category_image = db.Column(db.String(255))
    
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade='all, delete-orphan')

class Order(db.Model):
    __tablename__ = 'ORDERS'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id', ondelete='CASCADE'), nullable=False)
    order_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    return_reason = db.Column(db.Text)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'ORDER_ITEM'
    order_id = db.Column(db.Integer, db.ForeignKey('ORDERS.order_id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('PRODUCT.product_id', ondelete='CASCADE'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    sum_amount = db.Column(db.Numeric(10, 2), nullable=False)

class Cart(db.Model):
    __tablename__ = 'CART'
    user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('PRODUCT.product_id', ondelete='CASCADE'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

class Review(db.Model):
    __tablename__ = 'REVIEW'
    r_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    review_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('PRODUCT.product_id', ondelete='CASCADE'), nullable=False)
