# module logging
# noise reduction
# sample 10s, average and save
from huey import crontab
from huey.contrib.sqlitedb import SqliteHuey
import time
import requests

from flask import Flask
from models import db
from models.log import ModuleDataLog

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://thermouser:blackie@192.168.1.105/thermo"
db.init_app(app)

app.db = db
app.app_context().push()

huey = SqliteHuey("logger", filename="/var/www/thermo-logger/huey.db")

@huey.periodic_task(crontab(month="*", day="*", hour="*", minute="*", day_of_week="*"))
def get_average_module_readings():
    readings = {}
    count = 0
    # for a minute, read from all sensors
    for i in range(5):
        response = requests.get("http://192.168.1.105:1337/module/*/read")
        if response.status_code != 200:
            continue

        data = response.json()

        # aggregate all readings
        for result in data.get("results"):
            module = result.get("module")
            mod_id = module.get("id")
            reading = result.get("reading")
            if not reading:
                print("Null reading for module id " + mod_id)
                continue

            if not readings.get(mod_id):
                readings[mod_id] = { "co2": 0,
                                     "temp": 0,
                                     "humidity": 0,
                                     "set_temp": reading.get("setTemp")
                                     }

            readings[mod_id]["co2"] += reading["co2"]
            readings[mod_id]["temp"] += reading["currentTemp"]
            readings[mod_id]["humidity"] += reading["hum"]
            count += 1

        time.sleep(10)

    # Then average and save the result
    for key in readings:
        r = readings[key]
        r["co2"] /= count
        r["temp"] /= count
        r["humidity"] /= count

        log = ModuleDataLog()
        log.co2 = r["co2"]
        log.temperature = r["temp"]
        log.humidity = r["humidity"]
        log.set_temp = r["set_temp"]
        log.module_id = key
        app.db.session.add(log)

    app.db.session.commit()
