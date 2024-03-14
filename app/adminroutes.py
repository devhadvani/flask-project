"""
admin_routes.py
This file contains routes for the admin panel.
"""

import os
from werkzeug.utils import secure_filename
from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for
)
from .__init__ import app, db
from .models import Category, Subcategory, Product, Order, Admin
from functools import wraps
from werkzeug.security import check_password_hash

def admin_required(func):
    """
    Decorator to check if the user is logged in as admin.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'admin_login' not in session:
            return redirect(url_for('admin_login'))
        return func(*args, **kwargs)
    return decorated_function

@app.route("/admin")
@admin_required
def admin():
    """
    Admin dashboard displaying product, category, and subcategory data.
    """
    data = Product.query.all()
    category = Category.query.all()
    sub_category = Subcategory.query.all()
    return render_template(
        "admin/admin.html", product=data, category=category, sub_category=sub_category
    )

@app.route("/add_category", methods=["GET", "POST"])
@admin_required
def add_category():
    """
    Add category route for admin.
    """
    if request.method == "POST":
        id = request.form["id"]
        name = request.form["name"]
        add = Category(category_id=id, name=name)
        db.session.add(add)
        db.session.commit()
        return redirect("admin")

@app.route("/add_subcategory", methods=["GET", "POST"])
@admin_required
def add_subcategory():
    """
    Add subcategory route for admin.
    """
    if request.method == "POST":
        id = request.form["id"]
        name = request.form["name"]
        cid = request.form["category_id"]
        add = Subcategory(subcategory_id=id, name=name, category_id=cid)
        db.session.add(add)
        db.session.commit()
        return redirect("admin")

@app.route("/add_product", methods=["POST"])
@admin_required
def add_product():
    """
    Add product route for admin.
    """
    if request.method == "POST":
        name = request.form["product_name"]
        desc = request.form["description"]
        price = request.form["price"]
        quantity = request.form["stock_quantity"]
        cid = request.form["cid"]
        scid = request.form["scid"]
        image = request.files["image"]
        im = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], im))
        add = Product(
            name=name,
            description=desc,
            price=price,
            stock_quantity=quantity,
            category_id=cid,
            subcategory_id=scid,
            image_url=im,
        )
        db.session.add(add)
        db.session.commit()
        return redirect("admin")



@app.route("/delete/<string:id>", methods=["POST", "GET"])
@admin_required
def delete_product(id):
    # if request.method =="POST":
    obj = Product.query.get(id)
    if obj:
        db.session.delete(obj)
        db.session.commit()
        return redirect("/admin")


@app.route("/update/<string:id>", methods=["POST", "GET"])
@admin_required
def update_product(id):
    product = Product.query.get(id)
    category = Category.query.all()

    sub_category = Subcategory.query.all()
    if request.method == "POST":
        image = request.files["image"]
        if image:
            im = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], im))
            image_url = im
        else:
            image_url = product.image_url

        product.name = request.form["product_name"]
        product.description = request.form["description"]
        product.price = request.form["price"]
        product.stock_quantity = request.form["stock_quantity"]
        product.category_id = request.form["cid"]
        product.subcategory_id = request.form["scid"]
        product.image_url = image_url
        db.session.commit()
    return render_template(
        "admin/update_product.html",
        product=product,
        category=category,
        sub_category=sub_category,
    )

from collections import defaultdict

@app.route('/admin/orders', methods=['POST', 'GET'])
@admin_required
def admin_order():
    order_counts = defaultdict(int)
    if request.method == 'POST':
        selected_status = request.form.get('status')

        if selected_status == "All":
            orders = Order.query.all()
        elif selected_status:
            orders = Order.query.filter_by(status=selected_status).all()
        else:
            orders = Order.query.all()

        for order in orders:
            order_counts[order.status] += 1

    else:
        orders = Order.query.all()

        for order in orders:
            order_counts[order.status] += 1

    return render_template('admin/orders.html', orders=orders, order_counts=order_counts)

@app.route('/update_status/<string:id>',methods=['POST'])
@admin_required
def update_status(id):
    if request.method == "POST":
        status = Order.query.get(id)
        update_status = request.form['status']
        status.status = update_status
        db.session.commit()
        return redirect('/admin/orders')

@app.route('/admin/admin_login',methods=['GET','POST'])
def admin_login():  
    if 'admin_login' in session:
        return redirect('/admin')
    if request.method == "POST":
        username = request.form['email']
        password = request.form['password']

        user = Admin.query.filter_by(admin_name=username).first()
        if user and check_password_hash(user.password, password):
            session['admin_login'] = user
            return redirect('/admin')
    return render_template('admin/login.html')

@app.route('/admin_logout',methods=['GET','POST'])
@admin_required
def admin_logout():
    session.pop('admin_login', None)

    return redirect('/admin/login')