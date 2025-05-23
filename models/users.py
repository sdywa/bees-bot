from peewee import CharField, IntegerField, FloatField, DateField

from .base import BaseModel, db


class Users(BaseModel):
    id = IntegerField(null=False, primary_key=True)
    catwar_id = IntegerField(null=True)
    stage = IntegerField(null=False, default=0)

    def add(user_data):
        db.connect()
        user = Users.create(**user_data)
        db.close()

    def find(id):
        db.connect()
        user = None
        try:
            user = Users.get(Users.id == id)
        except Users.DoesNotExist:
            pass

        db.close()
        return user
