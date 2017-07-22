import mongoengine as me
import property
from mongo import Stock as s


def connect():
    return me.connect(property.DB_COLLECT, host=property.DB_HOST, port=property.DB_PORT)


def contains(trade_code):
    stock = s.Stock.objects(trade_code=trade_code)
    return stock


def stock_by_trade_code(trade_code):
    return s.Stock.objects(trade_code=trade_code).first()


