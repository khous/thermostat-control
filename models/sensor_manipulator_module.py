from models import db

import datetime

class SensorManipulatorModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    ipv4_address = db.Column(db.String(15), nullable=False)
    last_keep_alive_ping = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return 'Module Name:' % self.name
