from huey.contrib.sqlitedb import SqliteHuey
huey = SqliteHuey("logger", filename="/var/www/thermo-logger/huey.db")