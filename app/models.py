from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120))
    username = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return self.username


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Subcategory(db.Model):
    subcategory_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"))
    name = db.Column(db.String(100))
    category = db.relationship("Category", backref="subcategories")


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"))
    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategory.subcategory_id"))
    category = db.relationship("Category", backref="products")
    subcategory = db.relationship("Subcategory", backref="products")


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.product_id"))
    quantity = db.Column(db.Integer, default=1)
    user = db.relationship("Users", backref="cart")
    product = db.relationship("Product", backref="cart")


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String(50), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    user = db.relationship("Users", backref="address")
    # Define any additional methods or relationships here


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.product_id"))
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float)
    order_date = db.Column(db.DateTime)
    status = db.Column(db.String(50),default="Pending")
    product = db.relationship("Product", backref="order")
    user = db.relationship("Users", backref="order")
    address = db.relationship("Address", backref="order")


class Admin(db.Model):
    admin_name =db.Column(db.String(50),primary_key=True)
    password = db.Column(db.String(255), nullable=True)


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
