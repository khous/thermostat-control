from flask import jsonify, Flask
from models import db

def to_dict(model):
    my_attrs = model.__dict__.items()
    out_dict = {}

    for attr in my_attrs:
        if attr[0].startswith("_"):
            continue

        out_dict[attr[0]] = attr[1]

    return out_dict

def get_db():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://thermouser:blackie@192.168.1.105/thermo"
    db.init_app(app)

    app.db = db
    app.app_context().push()

    return db