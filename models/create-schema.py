from comm_gateway import app
from models import *

app.db.create_all("__all__", app)
