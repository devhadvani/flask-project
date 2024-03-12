# __init__.py

from flask import Flask
from .models import db
from flask_migrate import Migrate
from flask_caching import Cache
from flask_session import Session
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost:3306/online_store"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db


app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'

cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'  
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
Session(app)


db.init_app(app)
migrate = Migrate(app, db)

from .adminroutes import *
from .routes import *