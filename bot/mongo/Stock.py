from mongoengine import (Document, IntField, FloatField, StringField, DateTimeField, ListField, ObjectIdField)
import datetime
import extractor
import mongo.mongo as m

conn = m.connect()


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
    volume_stock_on_market = IntField()
    month_history = ListField()

    def stock_line(self, line):
        self.datestamp = datetime.datetime.utcnow()
        self.datestamp = line[0]
        self.currency = line[14]
        self.trade_code = line[7]
        self.emitent_full_name = line[11]
        self.capitalisation = float(extractor.get_value_capitalization(self.trade_code))
        self.free_float = float(extractor.get_free_float(self.trade_code))
        self.official_url = line[37]
        self.url = line[38]
        return self

    def __str__(self):
        return format("{"
                      "_id: %s,\n datestamp: %s,\n trade_code: %s,\n emitent_full_name: %s,\n"
                      "curency: %s,\n capitalisation: %s,\n free_float: %s,\n official_url: %s,\n"
                      "url: %s,\n short_name: %s,\n finame_em: %s\n}" %
                      (str(self._id), str(self.datestamp), self.trade_code, self.emitent_full_name,
                       str(self.currency), str(self.capitalisation), str(self.free_float), self.official_url,
                       self.url, self.short_name, self.finame_em))
