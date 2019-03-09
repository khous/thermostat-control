import datetime
from models import db


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(length=255), nullable=False, index=True)
    ts = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)
    value = db.Column(db.String(length=2048), nullable=False)

