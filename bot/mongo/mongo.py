import mongoengine as me
import property
from mongo import Stock as s
import my_log
import re
from mongo.exception import *

LOG = my_log.get_logger('mongo')


def connect():
    return me.connect(property.DB_COLLECT, host=property.DB_HOST, port=property.DB_PORT)


def extract_stock(stocks, parameter):
    if stocks.count() > 1:
        message = property.DB_CONTAINS_MORE_ONE % (stocks.count(), parameter)
        LOG.error(message)
        raise FoundMoreThanOneStock(message)
    elif stocks.count() == 1:
        return stocks.first()
    else:
        message = property.DB_NOT_FOUNT_STOCK % parameter
        LOG.error(message)
        raise NotFoundStock(message)


def stock_by_trade_code(trade_code):
    stocks = s.Stock.objects(trade_code=str(trade_code).upper())
    return extract_stock(stocks, trade_code)


def stock_by_emitet_name(name, is_priviliged=False):
    if is_priviliged:
        regex_trade_code = re.compile(r'^[A-Z]{5}$')
    else:
        regex_trade_code = re.compile(r'^[A-Z]{4}$')

    stocks = s.Stock.objects(emitent_full_name__icontains=name, trade_code=regex_trade_code)
    return extract_stock(stocks, name)
