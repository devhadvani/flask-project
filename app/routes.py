# routes.py

from flask import render_template, request, redirect
from .__init__ import app, db
from .models import Users, Category, Subcategory, Product
from werkzeug.utils import secure_filename
import os
# Define your routes here

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

print(os.getcwd)

@app.route('/')
def home():
    print(os.getcwd())

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
    data = Product.query.all()
    return render_template('admin/admin.html',product=data)

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
        print(im)
        print(os.path.join(app.config['UPLOAD_FOLDER'],im))


        image.save(os.path.join(app.config['UPLOAD_FOLDER'],im))
        image_url = os.path.join(app.config['UPLOAD_FOLDER'],im)

        add = Product(name= name, description= desc,price= price, stock_quantity= quantity,category_id=cid,subcategory_id=scid,image_url=im)
        # addimage = ProductImage(product_id =1,image_url = image)
        db.session.add(add)
        # db.session.add(addimage)
        db.session.commit()
        return redirect('admin')
    return redirect('admin')

@app.route('/delete/<string:id>',methods=['POST',"GET"])
def delete_product(id):
    # if request.method =="POST":
    obj = Product.query.get(id)
    if obj:
        db.session.delete(obj)
        db.session.commit()
        return redirect('/admin')
