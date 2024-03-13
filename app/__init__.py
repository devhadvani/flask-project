# __init__.py

from flask import Flask
from .models import db
from flask_migrate import Migrate
from flask_caching import Cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)
cache.init_app(app)

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost:3306/online_store"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

from .routes import *
from .adminroutes import *