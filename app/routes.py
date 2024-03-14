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
from .models import Users, Category, Subcategory, Product, Cart, Address, Order, Admin
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_login import current_user
from flask_caching import Cache
from flask_session import Session
from flask import g, send_file, render_template_string
from sqlalchemy import desc
from flask_mail import Mail, Message
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(app, config={"CACHE_TYPE": "SimpleCache"})
# cache = Cache(app)
# app.config['CACHE_TYPE'] = 'simple'
# app.config['CACHE_DEFAULT_TIMEOUT'] = 300
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db


mail = Mail(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "devhadvani147@gmail.com"
app.config["MAIL_PASSWORD"] = "ucos jxug lwhh xiyp"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

mail = Mail(app)

app.config["SECRET_KEY"] = "004f2af45d3a4e161a7dd2d17fdae47f"
Session(app)



def generate_bill(product_details):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750

    for product in product_details:
        c.drawString(50, y, f"Product Name: {product['name']}")
        c.drawString(50, y - 20, f"Quantity: {product['quantity']}")
        c.drawString(50, y - 40, f"Price: {product['price']}")
        y -= 60

    c.save()
    buffer.seek(0)

    return buffer


@app.route("/download_bill/<string:id>")
def download_bill(id):
    product = Order.query.get(id)

    product_details = [
        {
            "name": product.product.name,
            "quantity": product.quantity,
            "price": product.total_price,
        },
    ]

    pdf_buffer = generate_bill(product_details)
    return send_file(pdf_buffer, as_attachment=True, download_name="bill.pdf")
    return redirect("/my_orders")


class UserNotFoundError(Exception):
    def __init__(self, message="User not found in database", status_code=404):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


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
                raise UserNotFoundError()
            g.current_user = user
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return jsonify({"message": "Invalid token"}), 401
        except UserNotFoundError as e:
            return jsonify({"message": e.message}), e.status_code

    return decorated_function


@app.context_processor
@token_require
def cart_count():

    total_cart_count = Cart.query.filter_by(user_id=g.current_user.id).count()

    return dict(total_cart_count=total_cart_count)


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
    if current_user.is_authenticated:
        print("User is logged in.", current_user.id)
    else:
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
                {"public_id": user.email, "exp": datetime.utcnow() + timedelta(days=1)},
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
    # logout_user()
    session.pop("jwt_token", None)

    return redirect("/login")


@app.route("/shop", methods=["GET", "POST"])
@token_require
def shop_products():
    page = request.args.get("page", 1, type=int)
    print("current user id :-", g.current_user.id)
    print("current user email :-", g.current_user.email)
    print("current user  :-", g.current_user.username)
    name = request.args.get("s")

    if name:
        products = Product.query.filter(Product.name.like(f"%{name}%")).paginate(
            page=page, per_page=3
        )
    else:
        products = Product.query.paginate(page=page, per_page=3)
    return render_template("products.html", product=products, name=name)


@app.route("/shop/<string:id>")
# @cache.cached(timeout=300)
@token_require
def product_page(id):
    time = datetime.utcnow()
    print("Current time:", time)
    product = Product.query.get(id)
    user = g.current_user  # Retrieve the current user from the token_require decorator
    user_id = user.id
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
@token_require
def add_to_cart():
    if request.method == "POST":
        user_id = g.current_user.id
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
# @cache.cached(timeout=300)
@token_require
def cart():
    print("Current time:", datetime.utcnow())
    current_user = g.current_user
    address_count = Address.query.filter_by(user_id=g.current_user.id).count()
    address = Address.query.filter_by(user_id=g.current_user.id)
    cart_item = Cart.query.filter_by(user_id=g.current_user.id).all()
    return render_template(
        "cart.html", cart_item=cart_item, address=address, address_count=address_count
    )


@app.route("/update_quantity", methods=["POST"])
@token_require
def update_quantity():
    if request.method == "POST":
        action = request.form["action"]
        product_id = request.form["product_id"]
        quantity = request.form["quantity"]
        user_id = g.current_user.id
        cart = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()
        # # print(cart)
        if action == "increment":
            cart.quantity += 1
        else:
            cart.quantity -= 1
        db.session.commit()
        return redirect("cart")


@app.route("/remove_from_cart", methods=["POST"])
@token_require
def remove_from_cart():
    if request.method == "POST":
        product_id = request.form["product_id"]
        print("sfkjshfkjsdf", product_id)
        user_id = g.current_user.id
        cart = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()
        db.session.delete(cart)
        db.session.commit()
        return redirect("cart")


@app.route("/add_address", methods=["POST"])
@token_require
def add_address():
    if request.method == "POST":
        user_id = g.current_user.id
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


def send_order_confirmation_email(recipient_email, cart_items):
    msg = Message(
        subject="Order Confirmation",
        sender="devhadvani147@gmail.com",
        recipients=[recipient_email],
    )

    msg_body = "Thank you for your order!\n\n"
    msg_body += "Your order details:\n"

    for cart in cart_items:
        msg_body += f"Product: {cart.product.name}\n"
        msg_body += f"Quantity: {cart.quantity}\n"
        msg_body += f"Price: Rs.{cart.product.price}\n\n"

    after = datetime.now() + timedelta(days=2)
    msg_body += f"Your product will be delevered before { after.date() }  {after.strftime('%A')}\n"

    msg.body = msg_body

    mail.send(msg)


@login_required
@app.route("/check_out", methods=["GET", "POST"])
@token_require
def check_out():
    address = Address.query.filter_by(user_id=g.current_user.id)
    cart_item = Cart.query.filter_by(user_id=g.current_user.id)
    total = 0
    for cart_item2 in cart_item:
        total += cart_item2.product.price * cart_item2.quantity
    address_count = Address.query.filter_by(user_id=g.current_user.id).count()
    after = datetime.now() + timedelta(days=2)
    if request.method == "POST":
        user_id = g.current_user.id
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

        

        try:
            send_order_confirmation_email(g.current_user.email, cart_item)
            print("Order placed successfully. Confirmation email sent.", "success")
        except Exception as e:
            print(
                "Failed to send order confirmation email. Please contact support.",
                "error",
            )
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return redirect("/my_orders")
    return render_template(
        "checkout.html",
        address=address,
        cart_item=cart_item,
        address_count=address_count,
        after=after,
        total=total,
    )


@app.route("/my_orders")
@token_require
def my_orders():
    order = (
        Order.query.filter_by(user_id=g.current_user.id)
        .order_by(desc(Order.order_date))
        .all()
    )
    return render_template("myorders.html", order=order)


@app.route("/my_account")
@token_require
def account():
    user = g.current_user
    address = Address.query.filter_by(user_id=user.id)
    order = (
        Order.query.filter_by(user_id=user.id).order_by(desc(Order.order_date)).all()
    )
    return render_template("account.html", user=user, address=address, order=order)


@app.route("/remove_order/<string:id>", methods=["GET"])
@token_require
def remove_order(id):
    order = Order.query.get(id)
    db.session.delete(order)
    db.session.commit()
    return redirect("/my_account")


@app.route("/delete_address/<string:id>", methods=["GET"])
@token_require
def delete_address(id):
    order = Address.query.get(id)
    db.session.delete(order)
    db.session.commit()
    return redirect("/my_account")


@app.route("/update_address/<string:id>", methods=["GET", "POST"])
@token_require
def update_address(id):
    address = Address.query.get(id)
    if request.method == "POST":
        name = request.form["name"]
        street_address = request.form["street_address"]
        city = request.form["city"]
        state = request.form["state"]
        postal_code = request.form["postal_code"]
        country = request.form["country"]
        phone_number = request.form["phone_number"]
        is_default = bool(request.form.get("is_default"))

        address.name = name
        address.street_address = street_address
        address.city = city
        address.state = state
        address.postal_code = postal_code
        address.country = country
        address.phone_number = phone_number
        address.is_default = is_default

        db.session.commit()

        return redirect("/my_account")

    return render_template("update_address.html", address=address)
