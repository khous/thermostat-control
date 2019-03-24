import sys
from datetime import datetime, timedelta
import time
from sqlalchemy import and_
from models.log import Log
from models.aggregate_log import AggregateLog
from models.util import get_db
import sys

EPOCH = datetime.utcfromtimestamp(0)
db = get_db()

def to_sec(date):
    return (date - EPOCH).total_seconds()

def add_or_increment_entry(map, item):
    # Assume map is defined
    added = False
    if map.get(item) is not None:
        map[item] += 1
    else:
        added = True
        map[item] = 1

    return added


def calculate_occupancy(
        initial_status,
        logs,
        start_time_sec,
        end_time_sec
):
    total_timespan = end_time_sec - start_time_sec
    total_occupation = 0

    # Return whole value if the entire duration is occupied or unoccupied
    if len(logs) == 0:
        if initial_status == "occupied":
            return 1

        return 0

    current_status = initial_status
    last_status_change_sec = start_time_sec
    # Else calculate segments
    for l in logs:
        # Ain't care about duplicated states
        if l.value == current_status:
            continue

        # Otherwise it's a flip
        current_status = l.value

        if current_status == "unoccupied":
            # Add last time segment to total
            seg_length = (to_sec(l.ts) - last_status_change_sec)
            print("Adding {length} of occupancy".format(length=seg_length))
            total_occupation += (to_sec(l.ts) - last_status_change_sec)
        else:
            print("Length of inoccupancy is {length}".format(length=(to_sec(l.ts) - last_status_change_sec)))

        last_status_change_sec = to_sec(l.ts)


    # Add the trailing amount to the total
    if current_status == "occupied":
        total_occupation += (end_time_sec - last_status_change_sec)


    print("total occupation time is " + str(total_occupation))
    return total_occupation / total_timespan

def main(from_time, to_time):

    agg_log = AggregateLog()
    agg_log.dns_queries = {}
    agg_log.hosts = {}
    agg_log.total_dns_queries = agg_log.total_hosts = 0
    agg_log.from_time = from_time
    agg_log.to_time = to_time
    agg_log.day_of_month = from_time.day
    agg_log.day_of_week = from_time.weekday()
    agg_log.hour_of_day = from_time.hour
    agg_log.minute_of_hour = from_time.minute

    last_occupancy_status = Log.query\
        .filter(Log.type == "occupancy-status")\
        .filter(Log.ts < from_time)\
        .order_by(Log.ts.desc())\
        .first()

    # Default to occupied in the unlikely event that this is not found
    last_occupancy_status = \
        "occupied" if not last_occupancy_status else last_occupancy_status.value


    occupancy_logs = Log.query \
        .filter(and_(Log.ts >= from_time, Log.ts < to_time))\
        .filter(Log.type == "occupancy-status") \
        .order_by(Log.ts.asc()) \
        .all()

    # occupancy_total = len(occupancy_logs)
    # occupied_hits =
    # for l in occupancy_logs:

    agg_log.occupied = calculate_occupancy(last_occupancy_status, occupancy_logs, to_sec(from_time), to_sec(to_time))

    logs = Log.query\
        .filter(and_(Log.ts >= from_time, Log.ts < to_time))\
        .filter(Log.type.in_(["host-mac-address", "dns-query"]))\
        .all()

    # if not logs:
        # sys.exit(0)

    for l in logs:
        if l.type == "host-mac-address":
            if add_or_increment_entry(agg_log.hosts, l.value):
                agg_log.total_hosts += 1
        elif l.type == "dns-query":
            if add_or_increment_entry(agg_log.dns_queries, l.value):
                agg_log.total_dns_queries += 1

    db.session.add(agg_log)
    db.session.commit()

    print(len(logs))
    # Get all logs from time period


if __name__ == "__main__":
    first_log = AggregateLog.query.order_by(AggregateLog.to_time.desc()).first()

    if first_log:
        from_time = first_log.to_time
    else:
        from_time = Log.query.order_by(Log.ts.asc()).first().ts

    while from_time + timedelta(seconds=900) < datetime.utcnow():
        to_time = from_time + timedelta(seconds=900)
        main(from_time, to_time)
        print("We're at " + str(from_time))
        from_time += timedelta(seconds=900)