from mongoengine import (EmbeddedDocumentField, Document, IntField, FloatField, StringField, DateTimeField, ListField,
                         ObjectIdField)
import datetime
from datetime import timedelta
import bot.mongo.Price as price
from bot.mongo import exception


class Stock(Document):
    _id = ObjectIdField()
    datestamp = DateTimeField()
    instrument_id = IntField()
    list_section = IntField()
    rn = StringField()
    supertype = IntField()
    instrument_type = IntField()
    instrument_category = IntField()
    trade_code = StringField()
    isin = IntField()
    registry_number = IntField()
    registry_date = IntField()
    emitent_full_name = StringField()
    inn = IntField()
    nominal = IntField()
    currency = StringField()
    security_has_default = IntField()
    security_has_tech_default = IntField()
    capitalisation = FloatField()
    free_float = FloatField()
    official_url = StringField()
    url = StringField()
    files_name = ListField()
    short_name = StringField()
    finame_em = IntField()
    last_price = FloatField()
    volume_stock_on_market = FloatField()
    month_history = ListField(EmbeddedDocumentField(price.Price))
    week_history = ListField(EmbeddedDocumentField(price.Price))
    day_history = ListField(EmbeddedDocumentField(price.Price))
    hour_history = ListField(EmbeddedDocumentField(price.Price))
    lot = IntField()

    def __str__(self):
        return format("{"
                      "_id: %s,\n datestamp: %s,\n trade_code: %s,\n emitent_full_name: %s,\n"
                      "curency: %s}" %
                      (str(self._id), str(self.datestamp), self.trade_code, self.emitent_full_name,
                       str(self.currency)))

    def update_file(self, stock_file):
        self.datestamp = stock_file.datestamp
        self.instrument_id = stock_file.instrument_id
        self.list_section = stock_file.list_section
        self.rn = stock_file.rn
        self.supertype = stock_file.supertype
        self.instrument_type = stock_file.instrument_type
        self.instrument_category = stock_file.instrument_category
        self.trade_code = stock_file.trade_code
        self.isin = stock_file.isin
        self.registry_number = stock_file.registry_number
        self.registry_date = stock_file.registry_date
        self.emitent_full_name = stock_file.emitent_full_name
        self.inn = stock_file.inn
        self.nominal = stock_file.nominal
        self.currency = stock_file.currency
        self.security_has_default = stock_file.security_has_default
        self.security_has_tech_default = stock_file.security_has_tech_default
        self.capitalisation = stock_file.capitalisation
        self.free_float = stock_file.free_float
        self.official_url = stock_file.official_url
        self.url = stock_file.url
        self.files_name = stock_file.files_name
        self.short_name = stock_file.short_name
        self.finame_em = stock_file.finame_em
        self.last_price = stock_file.last_price
        self.volume_stock_on_market = stock_file.volume_stock_on_market
        self.month_history = stock_file.month_history
        self.week_history = stock_file.week_history
        self.day_history = stock_file.day_history
        self.hour_history = stock_file.hour_history
        self.lot = stock_file.lot

    def shape(self):
        return self.trade_code.upper() + '.ME'

    def get_day_price(self, date: datetime.datetime) -> float:
        for price in self.day_history:
            if date.date().weekday() == 5:
                date = date - timedelta(days=1)
            if date.date().weekday() == 6:
                date = date - timedelta(days=2)
            if price.date.date() == date.date():
                return price.value
        raise exception.NotFoundPrice('For stock %s not found price on %s' % (self.trade_code, str(date)))
