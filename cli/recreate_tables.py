from database import db
from models import tables

db.connect()
db.drop_tables(tables)
db.create_tables(tables)

print("Recreated!")

db.close()

