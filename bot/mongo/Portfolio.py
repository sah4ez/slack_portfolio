from mongoengine import (Document, EmbeddedDocumentField, FloatField, ListField, EmbeddedDocument, StringField,
                         ObjectIdField)


class Item(EmbeddedDocument):
    trade_code = StringField()
    exchange = StringField()
    value = FloatField()


class ItemPortfolio(EmbeddedDocument):
    returns = FloatField()
    standard_deviation = FloatField()
    sharpe_ratio = FloatField()
    stocks = ListField(EmbeddedDocumentField(Item))


class Portfolio(Document):
    _id = ObjectIdField()
    max_item = EmbeddedDocumentField(ItemPortfolio)
    min_item = EmbeddedDocumentField(ItemPortfolio)
