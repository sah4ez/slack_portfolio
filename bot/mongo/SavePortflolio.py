from mongo.Portfolio import Portfolio, Item

from mongoengine import (Document, EmbeddedDocumentField, FloatField, ListField, EmbeddedDocument, StringField,
                         ObjectIdField, DateTimeField, IntField)


class Transaction(Item):
    _id = ObjectIdField()
    date = DateTimeField()
    count_lot = IntField()


class SavePortfolio(Document):
    _id = ObjectIdField()
    date_save = DateTimeField()
    name = StringField()
    base_price = FloatField()
    current_price = FloatField()
    income = FloatField()
    user = StringField()
    transactions = ListField(EmbeddedDocumentField(Transaction))
