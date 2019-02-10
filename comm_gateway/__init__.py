from flask import Flask
from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://thermouser:blackie@192.168.1.105/thermo"
db.init_app(app)

app.db = db

from . import app as main_app