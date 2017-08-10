from mongo.Portfolio import Portfolio, Item

from mongoengine import (Document, EmbeddedDocumentField, FloatField, ListField, EmbeddedDocument, StringField,
                         ObjectIdField, DateTimeField, IntField)


class Transaction(Item):
    date = DateTimeField()
    count_lot = IntField()


class SavePortfolio(Portfolio):
    date_save = DateTimeField()
    name = StringField()
    base_price = FloatField()
    current_price = FloatField()
