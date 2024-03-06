from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    email = db.Column(db.String(120),primary_key=True)
    username = db.Column(db.String(80),nullable=True)
    password = db.Column(db.String(255),nullable=True)

    def __repr__(self):
        return self.username

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Subcategory(db.Model):
    subcategory_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    name = db.Column(db.String(100))
    category = db.relationship('Category', backref='subcategories')

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.subcategory_id'))
    category = db.relationship('Category', backref='products')
    subcategory = db.relationship('Subcategory', backref='products')

# class ProductImage(db.Model):
#     image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
#     image_url = db.Column(db.String(255))
#     product = db.relationship('Product', backref='images')
# class Order(db.Model):
#     order_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
#     order_date = db.Column(db.DateTime)
#     status = db.Column(db.String(50))
#     total_price = db.Column(db.Float)
#     user = db.relationship('User', backref='orders')

# class OrderItem(db.Model):
#     order_item_id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
#     product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
#     quantity = db.Column(db.Integer)
#     price_per_unit = db.Column(db.Float)
#     order = db.relationship('Order', backref='items')
#     product = db.relationship('Product', backref='order_items')

# db.create_all()