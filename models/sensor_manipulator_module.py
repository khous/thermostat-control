from models import db

import datetime

class SensorManipulatorModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    ipv4_address = db.Column(db.String(15), nullable=False)
    last_keep_alive_ping = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    config_id = db.Column(db.Integer, db.ForeignKey("module_config.id"), nullable=True, unique=True)
    config = db.relationship('ModuleConfig',
                             backref=db.backref('sensor_manipulator_module', lazy=False))

    def __repr__(self):
        return 'Module Name:' % self.name
