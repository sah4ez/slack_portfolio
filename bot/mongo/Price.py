from mongoengine import (Document, FloatField, DateTimeField)

import mongo.mongo as m

conn = m.connect()


class Price(Document):
    def __init__(self, datetime, value, *args, **values):
        super().__init__(*args, **values)
        self.date = datetime
        self.value = value

    date = DateTimeField(required=True)
    value = FloatField(required=True)

    def __str__(self):
        return format("Price = {\ndate: %s,\n value: %s\n}" % (str(self.date), str(self.value)))
