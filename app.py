from flask import Flask,render_template , request,redirect
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
# from .models import Users
app = Flask(__name__)


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost:3306/online_store"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)



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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "POST":
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print(name)
        print(email)
        print(password)
        user = Users(email=email, password=password,username=name)
        db.session.add(user)
        db.session.commit()

        return redirect('/')

    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/admin')
def admin():
    return render_template('admin/admin.html')

@app.route('/add_category',methods=['GET','POST'])
def add_category():

    if request.method == "POST":
        id = request.form['id']
        name = request.form['name']
        print(name)
        add = Category(category_id = id, name = name)
        db.session.add(add)
        db.session.commit()
        return redirect('admin')
    pass

@app.route('/add_subcategory',methods=['GET','POST'])
def add_subcategory():
    if request.method == "POST":
        id = request.form['id']
        name = request.form['name']
        cid = request.form['category_id']
        print(name)
        add = Subcategory(subcategory_id=id, name=name,category_id = cid)
        db.session.add(add)
        db.session.commit()
        return redirect('admin')
    pass


@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == "POST":
        name = request.form['product_name']
        desc = request.form['description']
        price = request.form['price']
        quantity = request.form['stock_quantity']
        cid = request.form['cid']
        scid = request.form['scid']
        image = request.files['image']
        print(image)
        print("image:",image.filename)
        im = secure_filename(image.filename)

        image.save(os.path.join(app.config['UPLOAD_FOLDER'],im))
        image_url = os.path.join(app.config['UPLOAD_FOLDER'],im)

        add = Product(name= name, description= desc,price= price, stock_quantity= quantity,category_id=cid,subcategory_id=scid,image_url=im)
        # addimage = ProductImage(product_id =1,image_url = image)
        db.session.add(add)
        # db.session.add(addimage)
        db.session.commit()
        return redirect('admin')
    return redirect('admin')


@app.route('/list')
def list_product():
    data = Product.query.all()
    return render_template('admin/admin.html', product=data)

if __name__ =="__main__":
    app.run(debug=True)