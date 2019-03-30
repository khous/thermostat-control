# module log_collection
# noise reduction
# sample 10s, average and save
import time
import re
from datetime import datetime
from subprocess import check_output
from huey import crontab

import requests

from flask import Flask
from models import db
from models.log import Log

from log_collection.config import huey


def get_db():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://thermouser:blackie@192.168.1.105/thermo"
    db.init_app(app)

    app.db = db
    app.app_context().push()

    return db


def parse_nmap_output(nmap_output):
    """
    Nmap scan report for 192.168.1.2
    Host is up (0.00027s latency).
    MAC Address: 24:A4:3C:20:62:CD (Ubiquiti Networks)
    """
    output = {}

    i = 0
    while i < len(nmap_output):
        line = nmap_output[i]
        print(line)
        if line.startswith("Nmap scan report for"):

            ip_addr = re.search("((\\d{1,3})\\.{0,1}){4,4}", line).group(0)
            host = output[ip_addr] = {}
            i += 2

            if i >= len(nmap_output):
                break

            line = nmap_output[i]

            if not line.startswith("MAC Address"):
                i -= 1
                continue
            print(line)
            host["mac"] = re.match("MAC Address: (.*) \\(", line).group(1)
            host["vendor"] = re.match("^.*\\((.*)\\)$", line).group(1)
            continue

        i += 1

    return output

# Fetch DNS queries from the last whatever and such and sync in the log table?
# FRom and until are seconds since epoch, not millis since epoch
# 192.168.1.105/admin/api.php?getAllQueries&from=1552354900&until=1552355047

class PiHoleQuery(object):

    def __init__(self, lookup, timestamp):
        self.lookup = lookup
        self.timestamp = timestamp

    def to_model(self):
        log = Log()
        log.type = "dns-query"
        log.value = self.lookup
        log.ts = datetime.utcfromtimestamp(int(self.timestamp))
        return log

def parse_phole_query(q):
    return PiHoleQuery(q[2], q[0])

@huey.periodic_task(crontab(month="*", day="*", hour="*", minute="*", day_of_week="*"))
def get_dns_queries():
    db = get_db()
    last_log = Log.query.filter_by(type="dns-query").order_by(Log.ts.desc()).first()

    if not last_log:
        val = 0
    else:
        epoch = datetime.utcfromtimestamp(0)
        val = (last_log.ts - epoch).total_seconds()

    try:
        last_sync_seconds = int(val)
    except (ValueError, TypeError):
        last_sync_seconds = 0


    now = int(time.time())
    dns_res = requests.get(
        "http://192.168.1.105/admin/api.php?getAllQueries&from={fromseconds}&until={until}"
            .format(fromseconds=last_sync_seconds, until=(now - 1))
    )

    dns_queries = dns_res.json()
    sesh = db.session
    for q in dns_queries.get("data"):
        query = parse_phole_query(q)
        sesh.add(query.to_model())

    sesh.commit()


@huey.periodic_task(crontab(month="*", day="*", hour="*", minute="*", day_of_week="*"))
def get_active_hosts():
    """
    Run NMAP to gather the active hosts on our network
    :return:
    """
    print("Running NMAP")
    nmap_output = check_output(["sudo", "nmap", "-sP", "--system-dns", "192.168.1.0/24"])
    print(nmap_output)
    nmap_output = nmap_output.decode()
    nmap_output = nmap_output.split("\n")

    output = parse_nmap_output(nmap_output)

    sesh = get_db().session
    for key in output.keys():
        val = output.get(key)
        log = Log()

        log.type = "host-ip-address"
        log.value = key
        sesh.add(log)

        mac = val.get("mac")
        vendor = val.get("vendor")

        if mac:
            log = Log()
            log.type = "host-mac-address"
            log.value = mac
            sesh.add(log)

        if vendor:
            log = Log()
            log.type = "host-vendor"
            log.value = vendor
            sesh.add(log)

    sesh.commit()


"""
{
    "results": [
        {
            "module": {
                "config_id": 1,
                "id": 2,
                "ipv4_address": "192.168.1.106",
                "last_keep_alive_ping": "Sat, 30 Mar 2019 20:38:30 GMT",
                "mac_address": "30:AE:A4:27:F7:08",
                "name": "office"
            },
            "reading": {
                "co2": 488,
                "currentTemp": 68.9,
                "hum": 37,
                "off_degrees": 20,
                "on": false,
                "on_degrees": 70,
                "setTemp": 50
            },
            "status_code": 200
        }
    ]
}"""

@huey.periodic_task(crontab(month="*", day="*", hour="*", minute="*", day_of_week="*"))
def get_atmospherics():
    # make request to office
    # log req
    response = requests.get("http://192.168.1.105:1337/module/office/read")
    data = response.json()

    if not data.get("results"):
        return

    office_reading = data["results"][0]["reading"]

    co2_log = Log()

    co2_log.type = "office-co2"
    co2_log.value = office_reading["co2"]

    sesh = get_db().session

    sesh.add(co2_log)

    temp_log = Log()

    temp_log.type = "office-temperature"
    temp_log.value = office_reading["currentTemp"]

    sesh.add(temp_log)

    sesh.commit()












