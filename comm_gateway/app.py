from . import app
from flask import request, jsonify
from datetime import datetime
from models import util
import requests
import json

from models.sensor_manipulator_module import SensorManipulatorModule
from models.module_config import ModuleConfig

@app.route("/keep-alive", methods=["POST"])
def post_keep_alive():
    data = request.get_json()
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

@app.route("/module/<mod_id>", methods=["PATCH"])
def update_module(mod_id):
    module = SensorManipulatorModule.query.filter_by(id=mod_id).first()

    if module is None:
        return "not found", 404

    data = request.json

    for k in data.keys():
        setattr(module, k, data[k])

    app.db.session.add(module)
    app.db.session.commit()

    return jsonify(util.to_dict(module))

@app.route("/module/<module_name>/read", methods=["GET"])
def read_module(module_name):
    if module_name == "*":
        modules = SensorManipulatorModule.query.all()
    else:
        modules = SensorManipulatorModule.query.filter_by(name=module_name).all()

    responses = []
    for mod in modules:
        res = requests.get("http://" + mod.ipv4_address + "/")
        reading = ""
        try:
            reading = json.loads(res.text, encoding="utf-8")
        except:
            pass

        mod_dict = util.to_dict(mod)
        del mod_dict["module_config"]

        responses.append({
            "module": mod_dict,
            "reading":  reading,
            "status_code": res.status_code
        })


    return jsonify({
        "results": responses
    })

@app.route("/module/<module_name>/<status>", methods=[""])
def turn_module_on_or_off(module_name, status):
    modules = SensorManipulatorModule.query


@app.route("/module/<module_id>/config", methods=["POST"])
def post_config(module_id):
    data = request.get_json()

    config = ModuleConfig.query\
        .join(SensorManipulatorModule)\
        .filter(SensorManipulatorModule.id == module_id).first()

    if config is None:
        config = ModuleConfig()
        config.module_id = module_id

    config.temperature = data.get("temperature", config.temperature)
    config.servo_on_degrees = data.get("servo_on_degrees", config.servo_on_degrees)
    config.servo_off_degrees = data.get("servo_off_degrees", config.servo_off_degrees)

    if config.servo_on_degrees <= config.servo_off_degrees:
        return "invalid request", 400

    app.db.session.add(config)
    app.db.session.commit()

    push_config(config.module, config)

    config_dict = util.to_dict(config)
    del config_dict["module"]

    return jsonify(config_dict)


def push_config(module, config):
    requests.post("http://" + module.ipv4_address + "/", data=json.dumps({
        "command": "set_temp",
        "temp": config.temperature
    }))

    requests.post("http://" + module.ipv4_address + "/", data=json.dumps({
        "command": "set_sweep",
        "on_degrees": config.servo_on_degrees,
        "off_degrees": config.servo_off_degrees
    }))





