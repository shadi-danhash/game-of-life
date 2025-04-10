from peewee import *

db = SqliteDatabase('game_of_life.db')

class Game(Model):
    name = CharField()

    class Meta:
        database = db

class Point(Model):
    game = ForeignKeyField(Game, backref='points')
    point = TextField()

    class Meta:
        database = db
