from models import db

class AggregateLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_time = db.Column(db.DateTime, nullable=False, index=True)
    to_time = db.Column(db.DateTime, nullable=False, index=True)
    day_of_month = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    hour_of_day = db.Column(db.Integer, nullable=False)
    minute_of_hour = db.Column(db.Integer, nullable=False)

    # Let this column hold a map of all sites accessed
    # Where
    #   key = website name
    #   Value = times accessed
    dns_queries = db.Column(db.JSON, nullable=False)
    total_dns_queries = db.Column(db.Integer, nullable=False)


    # Let this column hold a map of all hosts seen
    # Where
    #   key = host's MAC address
    #   value = number of times seen in the 15 minute window of this aggregation
    hosts = db.Column(db.JSON, nullable=False)
    total_hosts = db.Column(db.Integer, nullable=False)

    # The value of the last occupancy-status flag maybe?
    # Or a pctage duration for which the home was occupied during this 15 minute window
    # Use a percentage -- If this is problematic, it can be rounded to a bit value
    occupied = db.Column(db.Float, nullable=False)