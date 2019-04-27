from models.log import Log
from models.aggregate_co2_log import AggregateCO2Log
from models.util import get_db

def main():
    db = get_db()

    co2_logs = Log.query.filter(Log.type == "office-co2").order_by(Log.ts.desc())

    for l in co2_logs:
        agg_log = AggregateCO2Log()

        agg_log.co2_ppm = l.value
        agg_log.ts = l.ts
        agg_log.occupancy_status = Log.query\
            .filter(Log.ts < l.ts)\
            .filter(Log.type == "office-occupancy-status")\
            .order_by(Log.ts.desc())\
            .first().value

        agg_log = agg_log
        db.session.add(agg_log)

    db.session.commit()


if __name__ == "__main__":
    main()