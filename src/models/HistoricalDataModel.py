from peewee import *

db = db = SqliteDatabase(':memory:')


class HistoricalData(Model):
    date = CharField()
    open_price = CharField()
    high_price = CharField()
    low_price = CharField()
    close_price = CharField()
    adj_close = CharField()
    volume = CharField()

    class Meta:
        database = db