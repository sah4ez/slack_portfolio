from mongoengine import (EmbeddedDocument, FloatField, DateTimeField)


class Price(EmbeddedDocument):
    date = DateTimeField(required=True)
    value = FloatField(required=True)

    def __str__(self):
        return format("Price = {\ndate: %s,\n value: %s\n}" % (str(self.date), str(self.value)))
