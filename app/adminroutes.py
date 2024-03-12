import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect,jsonify, make_response,session,url_for
from .__init__ import app, db
from .models import Users, Category, Subcategory, Product,Cart, Address,Order
from datetime import datetime, timedelta


@app.route('/admin')
@login_required
def admin():
    data = Product.query.all()
    category = Category.query.all()
    sub_category = Subcategory.query.all()
    return render_template('admin/admin.html',product=data,category=category,sub_category=sub_category)


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

@app.route('/delete/<string:id>',methods=['POST',"GET"])
def delete_product(id):
    # if request.method =="POST":
    obj = Product.query.get(id)
    if obj:
        db.session.delete(obj)
        db.session.commit()
        return redirect('/admin')

@app.route('/update/<string:id>',methods=['POST',"GET"])
def update_product(id):
    product = Product.query.get(id)
    category = Category.query.all()
    sub_category = Subcategory.query.all()
    if request.method == "POST":
        product.name = request.form['product_name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.stock_quantity = request.form['stock_quantity']
        product.category_id = request.form['cid']
        product.subcategory_id = request.form['scid']
        db.session.commit()
    return render_template('admin/update_product.html',product=product,category=category,sub_category=sub_category)
