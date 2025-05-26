from peewee import CharField, IntegerField, BooleanField

from .base import BaseModel, db


class Users(BaseModel):
    catwar_id = IntegerField(null=True)
    stage = IntegerField(null=False, default=0)
    loner = BooleanField(default=False)

    @staticmethod
    def add(user_data):
        db.connect()
        user = Users.create(**user_data)
        db.close()
        return user

    @staticmethod
    def edit(id, new_data):
        user = Users.find(id)

        db.connect()
        for key in new_data:
            setattr(user, key, new_data[key])

        user.save()
        db.close()
        return user

    @staticmethod
    def find(id):
        db.connect()
        user = None
        try:
            user = Users.get(Users.id == id)
        except Users.DoesNotExist:
            pass

        db.close()
        return user
