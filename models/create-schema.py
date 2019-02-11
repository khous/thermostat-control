from comm_gateway import app
from models import sensor_manipulator_module, module_config

app.db.create_all("__all__", app)
