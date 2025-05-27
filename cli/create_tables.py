from database import db
from models import tables

db.connect()
db.create_tables(tables)

print("Created!")

db.close()

