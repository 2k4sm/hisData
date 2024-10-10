from peewee import *

db = SqliteDatabase('historical_data.db')


class HistoricalData(Model):
    date = CharField()
    open_price = CharField()
    high_price = CharField()
    low_price = CharField()
    close_price = CharField()
    adj_close = CharField()
    volume = CharField()
    from_currency = CharField()
    to_currency = CharField()
    start_date = CharField()
    end_date = CharField()
    period = CharField()

    class Meta:
        database = db