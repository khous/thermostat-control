from models import db


class ModuleConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False, default=68)
    servo_on_degrees = db.Column(db.Integer, nullable=False, default=70)
    servo_off_degrees = db.Column(db.Integer, nullable=False, default=20)

    module_id = db.Column(db.Integer, db.ForeignKey("sensor_manipulator_module.id"), nullable=False, unique=True)
    module = db.relationship('SensorManipulatorModule',
                               backref=db.backref('module_config', lazy=False))

    def __repr__(self):
        return 'Module Name:' % self.module.name