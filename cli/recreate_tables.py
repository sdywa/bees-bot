import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from database import db
from models import tables

db.connect()
db.drop_tables(tables)
db.create_tables(tables)

print("Recreated!")

db.close()

