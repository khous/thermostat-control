from models import db


class ModuleConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False, default=68)
    on_temperature = db.Column(db.Float, nullable=False, default=68)
    off_temperature = db.Column(db.Float, nullable=False, default=50)
    servo_on_degrees = db.Column(db.Integer, nullable=False, default=70)
    servo_off_degrees = db.Column(db.Integer, nullable=False, default=20)

    def __repr__(self):
        return 'Module Name:' % self.id