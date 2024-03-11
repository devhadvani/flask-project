'''
routes.py
this is routes.py file
'''

# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
import os
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect,jsonify
from .__init__ import app, db
from .models import Users, Category, Subcategory, Product,Cart, Address
import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required
# Define your routes here
from flask_login import current_user



UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'


print(os.getcwd)

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

login_manager = LoginManager()
login_manager.init_app(app)
# db.init_app(app)
 

# with app.app_context():
#     db.delete_all()
#     db.create_all()
 
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

@app.route('/')
def home():
    '''     
     will show home page of the website
    '''
    # Check if user is logged in
    if current_user.is_authenticated:
        # User is logged in
        print("User is logged in.",current_user.id)
    else:
        # User is not logged in
        print("User is not logged in.")
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    '''
    this function will handle a registration logic.
    user will enter name,email,password and it will store in database
    '''
    if request.method == "POST":
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        harshed_password = generate_password_hash(password,method='pbkdf2:sha256')
        user = Users(email=email, password=harshed_password,username=name)
        db.session.add(user)
        db.session.commit()

        return redirect('/')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', message='Username and password are required', alert_type='danger')

        user = Users.query.filter_by(email=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
        # if user and check_password_hash(user.password, password):
        #     token = jwt.encode({'public_id': user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], algorithm='HS256')
            # return jsonify({'token': token})
            # request.header = token
            # return render_template('/index.html', token=token)

        return render_template('login.html', message='Invalid username or password', alert_type='danger')

    return render_template('login.html', message='', alert_type='info')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

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
@login_required
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

@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop_products():
    page = request.args.get('page', 1, type=int)
    name = request.args.get('s')

    if name:
        products = Product.query.filter(Product.name.like(f"%{name}%")).paginate(page=page, per_page=2)
    else:
        products = Product.query.paginate(page=page, per_page=2)
    return render_template('products.html', product=products, name=name)

@app.route('/shop/<string:id>')
def product_page(id):
    product = Product.query.get(id)
    user_id = current_user.id
    product_in_cart = Cart.query.filter_by(user_id=user_id, product_id=id).first() is not None
    return render_template('product_page.html',product=product, cart = product_in_cart)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')
# @app.route('/search',methods=['GET','POST'])
# def search():
#     name = request.args.get('s')
#     print(name)
#     product = Product.query.filter(Product.name.like("%" + name + "%")).all()
#     print(product)
#     return render_template("/products.html",product=product,name=name)


@login_required
@app.route('/add_to_cart',methods=['POST'])
def add_to_cart():
    if request.method =="POST":
        user_id = current_user.id
        product_id  = request.form['product_id']
        exist_product = Cart.query.filter_by(user_id=user_id,product_id=product_id).first()
        if exist_product:
            return redirect('/cart')
        quantity = request.form['quantity']
        
        cart = Cart(user_id = user_id, quantity = quantity,product_id=product_id)
        db.session.add(cart)
        db.session.commit()
        return redirect('/shop/'+product_id)

@login_required
@app.route('/cart',methods=['POST','GET'])
def cart():
    address_count = Address.query.filter_by(user_id=current_user.id).count()
    address = Address.query.filter_by(user_id=current_user.id)
    cart_item = Cart.query.filter_by(user_id= current_user.id)
    return render_template('cart.html',cart_item=cart_item,address=address,address_count=address_count)




@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    if request.method == "POST":
        action = request.form['action']
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        user_id  = current_user.id
        cart  = Cart.query.filter_by(product_id=product_id, user_id = user_id).first()
        # # print(cart)
        if action == "increment":
            cart.quantity += 1
        else:
            cart.quantity -=1
        db.session.commit()
        return redirect('cart')


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if request.method == "POST":
        product_id = request.form['product_id']
        print("sfkjshfkjsdf",product_id)
        user_id  = current_user.id
        cart  = Cart.query.filter_by(product_id=product_id, user_id = user_id).first()
        db.session.delete(cart)
        db.session.commit()
        return redirect('cart')

@app.route('/add_address',methods=['POST'])
def add_address():
    if request.method=="POST":
        user_id  = current_user.id
        name = request.form['name']
        street_address = request.form['street_address']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal_code']
        country = request.form['country']
        phone_number = request.form['phone_number']
        is_default = bool(request.form.get('is_default'))

        address  = Address(user_id= user_id,name=name,street_address=street_address,city=city,state=state,country=country,postal_code=postal_code,phone_number=phone_number,is_default=is_default)
        db.session.add(address)
        db.session.commit()
        return redirect('/cart')



