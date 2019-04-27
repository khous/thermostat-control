from models import db

class AggregateCO2Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, nullable=False, index=True)
    co2_ppm = db.Column(db.Integer, nullable=False)
    occupancy_status = db.Column(db.String, nullable=False)
