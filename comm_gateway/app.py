from . import app
from flask import request, jsonify
from datetime import datetime

from models.sensor_manipulator_module import SensorManipulatorModule
from models.module_config import ModuleConfig

@app.route("/keep-alive", methods=["POST"])
def post_keep_alive():
    data = request.json
    mac = data["mac"]
    ip = data["ip"]

    module = SensorManipulatorModule.query.filter_by(mac_address=mac).first()

    if module is None:
        module = SensorManipulatorModule()
        module.ipv4_address = ip
        module.mac_address = mac
        module.name = "Unknown"
    else:
        module.last_keep_alive_ping = datetime.utcnow()


    app.db.session.add(module)
    app.db.session.commit()

    return "ok"