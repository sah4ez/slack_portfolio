from datetime import datetime, timedelta

import mongoengine as me
from mongoengine.connection import disconnect as closeDb
import property
from mongo import Stock as s
import my_log
import re
import random

from mongo.Portfolio import Portfolio
from mongo.exception import *

LOG = my_log.get_logger('mongo')


def connect():
    return me.connect(property.DB_COLLECT, host=property.DB_HOST, port=property.DB_PORT)


def close():
    return closeDb(property.DB_COLLECT)


def extract_stock(stocks, parameter):
    if stocks.count() > 1:
        message = property.DB_CONTAINS_MORE_ONE % (stocks.count(), parameter)
        LOG.error(message)
        close()
        raise FoundMoreThanOneStock(message)
    elif stocks.count() == 1:
        return stocks.first()
    else:
        message = property.DB_NOT_FOUNT_STOCK % parameter
        LOG.error(message)
        close()
        raise NotFoundStock(message)


def stock_by_trade_code(trade_code):
    connect()
    regex_trade_code = re.compile(r'(?i)^' + trade_code + '$')
    stocks = s.Stock.objects(trade_code=regex_trade_code)
    stock = extract_stock(stocks, trade_code)
    close()
    return stock


def stock_by_emitet_name(name, is_privileged=False):
    connect()
    regex_trade_code = get_regex_trade_code(is_privileged)
    stocks = s.Stock.objects(emitent_full_name__icontains=name, trade_code=regex_trade_code)
    stock = extract_stock(stocks, name)
    close()
    return stock


def get_regex_trade_code(is_privileged):
    return re.compile(property.PRIVILEGED) if is_privileged else re.compile(property.NOT_PRIVILEGED)


def get_n_first_portfolios(count: int):
    portfolios = list()
    connect()
    today = datetime.today() - timedelta(hours=12)
    for p in Portfolio.objects(date__gt=today).order_by('-max_item.sharpe_ratio')[:count]:
        portfolios.append(p)
    close()
    LOG.info('Loading %d portfolios' % len(portfolios))
    return portfolios


def get_n_random_portfolios():
    portfolios = list()
    connect()
    today = datetime.today() - timedelta(hours=12)
    found_portfolios = Portfolio.objects(date__gt=today).order_by('-max_item.sharpe_ratio')
    all_found = len(found_portfolios)
    for x in range(10):
        position = random.randint(0, all_found - 1)
        portfolios.append(found_portfolios[position])
    close()
    LOG.info('Loading %d portfolios' % len(portfolios))
    return portfolios
