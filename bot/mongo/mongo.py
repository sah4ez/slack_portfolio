import mongoengine as me
import property
from mongo import Stock as s
import my_log

LOG = my_log.get_logger('mongo')


def connect():
    return me.connect(property.DB_COLLECT, host=property.DB_HOST, port=property.DB_PORT)


def stock_by_trade_code(trade_code):
    stocks = s.Stock.objects(trade_code=str(trade_code).upper())
    stock = None
    if stocks.count() == 0:
        stock = s.Stock()
    elif stocks.count() == 1:
        stock = stocks.first()
    else:
        LOG.error("Collection contains %d the same document" % stocks.count())
        raise ValueError('Found %d stocks, should be one the stock' % int(stocks.count()))
    return stock
