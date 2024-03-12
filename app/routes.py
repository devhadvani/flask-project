"""
routes.py
this is routes.py file
"""

# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
import os
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import (
    render_template,
    request,
    redirect,
    jsonify,
    make_response,
    session,
    url_for,
)
from .__init__ import app, db
from .models import Users, Category, Subcategory, Product, Cart, Address, Order
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_login import current_user

# def token_required(f):
#    @wraps(f)
#    def decorator(*args, **kwargs):
#        token = None
#        if 'x-access-tokens' in request.headers:
#            token = request.headers['x-access-tokens']

#        if not token:
#            return jsonify({'message': 'a valid token is missing'})
#        try:
#            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
#            current_user = Users.query.filter_by(public_id=data['public_id']).first()
#        except:
#            return jsonify({'message': 'token is invalid'})

#        return f(current_user, *args, **kwargs)
#    return decorator


def token_require(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("jwt_token")
        if not token:
            return redirect(url_for("login"))

        try:
            decoded_token = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            email = decoded_token["public_id"]
            user = Users.query.filter_by(email=email).first()
            if not user:
                return jsonify({"message": "User not found"}), 404

            # Pass the user object to the wrapped function
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return jsonify({"message": "Invalid token"}), 401

    return decorated_function


login_manager = LoginManager()
login_manager.init_app(app)
# db.init_app(app)


# with app.app_context():
#     db.delete_all()
#     db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route("/")
def home():
    """
    will show home page of the website
    """
    # Check if user is logged in
    if current_user.is_authenticated:
        # User is logged in
        print("User is logged in.", current_user.id)
    else:
        # User is not logged in
        print("User is not logged in.")
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    this function will handle a registration logic.
    user will enter name,email,password and it will store in database
    """
    if request.method == "POST":
        name = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        harshed_password = generate_password_hash(password, method="pbkdf2:sha256")
        user = Users(email=email, password=harshed_password, username=name)
        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]

        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400

        user = Users.query.filter_by(email=username).first()
        if user and check_password_hash(user.password, password):
            token = jwt.encode(
                {
                    "public_id": user.email,
                    "exp": datetime.utcnow() + timedelta(minutes=45),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            response = make_response(redirect("/shop"))
            session["jwt_token"] = token
            return response
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route("/shop", methods=["GET", "POST"])
@cache.cached(timeout=300)
# @login_required
@token_require
def shop_products(current_user):
    page = request.args.get("page", 1, type=int)
    print("current user id :-", current_user.id)
    print("current user email :-", current_user.email)
    print("current user  :-", current_user.username)
    name = request.args.get("s")

    if name:
        products = Product.query.filter(Product.name.like(f"%{name}%")).paginate(
            page=page, per_page=20
        )
    else:
        products = Product.query.paginate(page=page, per_page=20)
    return render_template("products.html", product=products, name=name)


@app.route("/shop/<string:id>")
@cache.cached(timeout=300)
def product_page(id):
    time = datetime.utcnow()
    print("Current time:", time)
    product = Product.query.get(id)
    user_id = current_user.id
    product_in_cart = (
        Cart.query.filter_by(user_id=user_id, product_id=id).first() is not None
    )
    return render_template("product_page.html", product=product, cart=product_in_cart)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/login")


# @app.route('/search',methods=['GET','POST'])
# def search():
#     name = request.args.get('s')
#     print(name)
#     product = Product.query.filter(Product.name.like("%" + name + "%")).all()
#     print(product)
#     return render_template("/products.html",product=product,name=name)


@login_required
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if request.method == "POST":
        user_id = current_user.id
        product_id = request.form["product_id"]
        exist_product = Cart.query.filter_by(
            user_id=user_id, product_id=product_id
        ).first()
        if exist_product:
            return redirect("/cart")
        quantity = request.form["quantity"]

        cart = Cart(user_id=user_id, quantity=quantity, product_id=product_id)
        db.session.add(cart)
        db.session.commit()
        return redirect("/shop/" + product_id)


@login_required
@app.route("/cart", methods=["POST", "GET"])
@cache.cached(timeout=300)
def cart():
    print("Current time:", datetime.utcnow())
    address_count = Address.query.filter_by(user_id=current_user.id).count()
    address = Address.query.filter_by(user_id=current_user.id)
    cart_item = Cart.query.filter_by(user_id=current_user.id)
    return render_template(
        "cart.html", cart_item=cart_item, address=address, address_count=address_count
    )


@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    if request.method == "POST":
        action = request.form["action"]
        product_id = request.form["product_id"]
        quantity = request.form["quantity"]
        user_id = current_user.id
        cart = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()
        # # print(cart)
        if action == "increment":
            cart.quantity += 1
        else:
            cart.quantity -= 1
        db.session.commit()
        return redirect("cart")


@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    if request.method == "POST":
        product_id = request.form["product_id"]
        print("sfkjshfkjsdf", product_id)
        user_id = current_user.id
        cart = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()
        db.session.delete(cart)
        db.session.commit()
        return redirect("cart")


@app.route("/add_address", methods=["POST"])
def add_address():
    if request.method == "POST":
        user_id = current_user.id
        name = request.form["name"]
        street_address = request.form["street_address"]
        city = request.form["city"]
        state = request.form["state"]
        postal_code = request.form["postal_code"]
        country = request.form["country"]
        phone_number = request.form["phone_number"]
        is_default = bool(request.form.get("is_default"))

        address = Address(
            user_id=user_id,
            name=name,
            street_address=street_address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            phone_number=phone_number,
            is_default=is_default,
        )
        db.session.add(address)
        db.session.commit()
        return redirect("/cart")


@login_required
@app.route("/check_out", methods=["GET", "POST"])
def check_out():
    address = Address.query.filter_by(user_id=current_user.id)
    cart_item = Cart.query.filter_by(user_id=current_user.id)
    if request.method == "POST":
        user_id = current_user.id
        address_id = request.form["selected_address"]
        order_date = datetime.now()

        for cart in cart_item:
            order = Order(
                address_id=address_id,
                user_id=user_id,
                product_id=cart.product_id,
                quantity=cart.quantity,
                total_price=cart.product.price * cart.quantity,
                order_date=order_date,
            )
            db.session.add(order)
            db.session.delete(cart)
        db.session.commit()
    return render_template("checkout.html", address=address, cart_item=cart_item)


@app.route("/my_orders")
def my_orders():
    order = Order.query.filter_by(user_id=current_user.id)
    return render_template("myorders.html", order=order)