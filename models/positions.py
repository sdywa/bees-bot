from peewee import CharField, ForeignKeyField, IntegerField

from .base import BaseModel, db
from .users import Users


class Positions(BaseModel):
    user = ForeignKeyField(Users, backref='positions')
    title = CharField(null=False)

    @staticmethod
    def add(position_data):
        db.connect()
        position = Positions.create(**position_data)
        db.close()
        return position

    @staticmethod
    def remove(id):
        position = Positions.find(id)
        db.connect()
        position.delete_instance()
        db.close()

    @staticmethod
    def find(id):
        db.connect()
        position = None
        try:
            position = Positions.get(Positions.id == id)
        except Positions.DoesNotExist:
            pass

        db.close()
        return position

    @staticmethod
    def find_all(user_id):
        db.connect()
        positions = list(Positions.select().where(Positions.user_id == user_id))
        db.close()
        return positions
