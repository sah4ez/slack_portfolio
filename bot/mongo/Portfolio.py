from mongoengine import (Document, EmbeddedDocumentField, FloatField, ListField, EmbeddedDocument, StringField,
                         ObjectIdField)


class Item(EmbeddedDocument):
    trade_code = StringField()
    exchange = StringField()
    value = FloatField()

    def __str__(self):
        return '%s.%s %s' % (self.trade_code, self.exchange, str(self.value))


class ItemPortfolio(EmbeddedDocument):
    returns = FloatField()
    standard_deviation = FloatField()
    sharpe_ratio = FloatField()
    stocks = ListField(EmbeddedDocumentField(Item))


class Portfolio(Document):
    _id = ObjectIdField()
    max_item = EmbeddedDocumentField(ItemPortfolio)
    min_item = EmbeddedDocumentField(ItemPortfolio)

    def print_stocks(self) -> str:
        return str(self._id) + " ".join(self.max_item.stocks) + '\n' + " ".join(self.min_item.stocks)