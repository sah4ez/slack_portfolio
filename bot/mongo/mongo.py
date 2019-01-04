from datetime import datetime, timedelta

import mongoengine as me
from mongoengine.connection import disconnect as closeDb
from bot.property import DB_NOT_FOUNT_STOCK, NOT_PRIVILEGED, DB_CONTAINS_MORE_ONE, PRIVILEGED
import bot.mongo
from bot.my_log import get_logger
import re
import random
from os import environ as env

from bot.mongo.Portfolio import Portfolio
from bot.mongo.exception import *

LOG = get_logger('mongo')


def connect():
    return me.connect(env.get('DB_NAME_ENV'), host=env.get('DB_HOST'), port=int(env.get('DB_PORT')))


def close():
    return closeDb(env.get('DB_NAME_ENV'))


def extract_stock(stocks, parameter):
    if stocks.count() > 1:
        message = DB_CONTAINS_MORE_ONE % (stocks.count(), parameter)
        LOG.error(message)
        close()
        raise FoundMoreThanOneStock(message)
    elif stocks.count() == 1:
        return stocks.first()
    else:
        message = DB_NOT_FOUNT_STOCK % parameter
        LOG.error(message)
        close()
        raise NotFoundStock(message)


def stock_by_trade_code(trade_code):
    connect()
    regex_trade_code = re.compile(r'(?i)^' + trade_code + '$')
    stocks = bot.mongo.Stock.Stock.objects(trade_code=regex_trade_code)
    stock = extract_stock(stocks, trade_code)
    close()
    return stock


def stock_by_emitet_name(name, is_privileged=False):
    connect()
    regex_trade_code = get_regex_trade_code(is_privileged)
    stocks = bot.mongo.Stock.Stock.objects(emitent_full_name__icontains=name, trade_code=regex_trade_code)
    stock = extract_stock(stocks, name)
    close()
    return stock


def get_regex_trade_code(is_privileged):
    return re.compile(PRIVILEGED) if is_privileged else re.compile(NOT_PRIVILEGED)


def get_n_first_portfolios(count: int):
    portfolios = list()
    connect()
    today = datetime.today() - timedelta(hours=12)
    for p in Portfolio.objects(date__gt=today).order_by('-max_item.sharpe_ratio')[:count]:
        portfolios.append(p)
    close()
    LOG.info('Loading %d portfolios' % len(portfolios))
    return portfolios


def get_portfolio_by_id(id: str):
    portfolios = list()
    connect()
    portfolio = Portfolio.objects(_id=id).first()
    portfolios.append(portfolio)
    close()
    LOG.info('Loading %d portfolios' % len(portfolios))
    return portfolios


def get_n_random_portfolios(number=10):
    portfolios = list()
    connect()
    today = datetime.today() - timedelta(hours=12)
    found_portfolios = Portfolio.objects(date__gt=today).order_by('-max_item.sharpe_ratio')
    all_found = len(found_portfolios)
    for x in range(number):
        position = random.randint(0, all_found - 1)
        portfolios.append(found_portfolios[position])
    close()
    LOG.info('Loading %d portfolios' % len(portfolios))
    return portfolios
