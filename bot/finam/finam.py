import datetime as datetime
import re

from dateutil import relativedelta

from bot.config import RSP_FINAM_CODE_ALL
import bot.mongo.Price as p
import bot.mongo.mongo as db
from bot.my_log import get_logger
import bot.property as property
from bot.mongo.mongo import connect, close
from bot.mongo import Stock as s
from bot.resources.loader import download_file

LOG = get_logger("Finam Loader")


def set_price(stock, price, period):
    if period == property.FINAM_P_MONTH:
        stock.month_history.append(price)
    elif period == property.FINAM_P_WEEK:
        stock.week_history.append(price)
    elif period == property.FINAM_P_DAY:
        stock.day_history.append(price)
    elif period == property.FINAM_P_HOUR:
        stock.hour_history.append(price)


def get_date_from(period):
    if period == property.FINAM_P_WEEK:
        return datetime.datetime.now() - datetime.timedelta(days=property.FINAM_SHIFT_WEEK)
    elif period == property.FINAM_P_DAY:
        return datetime.datetime.now() - datetime.timedelta(days=property.FINAM_SHIFT_DAY)
    elif period == property.FINAM_P_HOUR:
        return datetime.datetime.now() - datetime.timedelta(hours=property.FINAM_SHIFT_HOUR)
    else:
        return datetime.datetime.now() - datetime.timedelta(days=property.FINAM_SHIFT_MONTH)


def shift_date_past(day_from, period, skips):
    date = day_from
    if period == property.FINAM_P_WEEK:
        date -= datetime.timedelta(weeks=skips)
    elif period == property.FINAM_P_DAY:
        date -= datetime.timedelta(days=skips)
    elif period == property.FINAM_P_HOUR:
        date -= datetime.timedelta(hours=skips)
    else:
        date -= relativedelta.relativedelta(months=skips)
    return date


def shift_date_future(day_from, period):
    date = day_from
    if period == property.FINAM_P_WEEK:
        date += datetime.timedelta(weeks=1)
    elif period == property.FINAM_P_DAY:
        date += datetime.timedelta(days=1)
    elif period == property.FINAM_P_HOUR:
        date += datetime.timedelta(hours=1)
    else:
        date += relativedelta.relativedelta(months=1)
    return date


def url_download_history_stock_price(trade_code, finam_em, file_name, period, from_day=1, from_month=1, from_year=2010,
                                     extention='.csv'):
    now = datetime.datetime.now()
    cur_day = now.day
    cur_month = now.month
    cur_year = now.year
    history_stock = 'http://export.finam.ru/' + file_name + extention + \
                    '?market=1' \
                    '&em=' + str(finam_em) + \
                    '&code=' + str(trade_code) + \
                    '&apply=0' \
                    '&df=' + str(from_day) + \
                    '&mf=' + str(from_month - 1) + \
                    '&yf=' + str(from_year) + \
                    '&from=' + format('%.2d' % from_day) + '.' + format('%.2d' % from_month) + '.' + str(from_year) + \
                    '&dt=' + str(cur_day) + \
                    '&mt=' + str(cur_month - 1) + \
                    '&yt=' + str(cur_year) + \
                    '&to=' + format('%.2d' % cur_day) + '.' + format('%.2d' % cur_month) + '.' + str(cur_year) + \
                    '&p=' + str(period) + \
                    '&f=' + str(file_name) + \
                    '&e=' + str(extention) + \
                    '&cn=' + str(trade_code) + \
                    '&dtf=4' \
                    '&tmf=3' \
                    '&MSOR=1' \
                    '&mstime=on' \
                    '&mstimever=1' \
                    '&sep=1' \
                    '&sep2=1' \
                    '&datf=1' \
                    '&at=1'
    return history_stock


def save_to_db(stock, finance_history, period, day_from):
    LOG.info("Save history %s to DB" % stock.trade_code)
    if period == property.FINAM_P_MONTH:
        day_from = datetime.datetime(day_from.year, day_from.month, 1)
    if period == property.FINAM_P_WEEK:
        day_from -= datetime.timedelta(days=day_from.weekday())
    date_from = day_from.date()
    text = ''
    try:
        with open(file=finance_history, mode='r', encoding='UTF-8') as file:
            text = file.read()
    except FileNotFoundError:
        LOG.error('Nof found file %s' % finance_history)

    skips = 0
    value = 0
    while date_from <= datetime.date.today():
        if date_from.weekday() in [5, 6] and period != property.FINAM_P_MONTH:
            date_from += datetime.timedelta(days=1)
            continue

        date = date_from.strftime('%d/%m/%y')
        pattern = re.compile(r'[A-Z]{4,5},[DWM],' + date + ',00:00:00,[0-9.]+,[0-9.]+,[0-9.]+,[0-9.]+,[0-9.]+')
        found = pattern.search(text)

        if found is not None and found.group():
            value = found.group().split(',')[7]
            save_skip_price(skips, value, date_from, period, stock)
            skips = 0
        else:
            skips += 1

        date_from = shift_date_future(date_from, period)
    if skips != 0:
        save_skip_price(skips, value, date_from, period, stock)


def save_skip_price(skips, value, date_from, period, stock):
    for skip in range(skips, -1, -1):
        price = p.Price()
        price.value = float(value)
        price.date = shift_date_past(date_from, period, skip)
        set_price(stock, price, period)


def process_by_period(stock, period):
    history_file_name = stock.trade_code + '_' + period
    date_from = get_date_from(period)
    url = url_download_history_stock_price(stock.trade_code,
                                           stock.finame_em,
                                           history_file_name,
                                           period=period,
                                           from_day=date_from.day,
                                           from_month=date_from.month,
                                           from_year=date_from.year)
    path = property.TYPE2_PATH + '/' + stock.trade_code + '/' + history_file_name + '.csv'
    LOG.info('Start loading hystory for %s from %s' % (stock.trade_code, url))
    size_download = download_file(url, path) / 1024
    LOG.info('Load %.2f Кб' % size_download)
    try:
        save_to_db(stock, path, period, date_from)
    except UnicodeDecodeError:
        LOG.error('Don\'t save %s with %s period with file %s on date %s' % (
            stock.trade_code, period, path, str(date_from)))
    finally:
        return stock.trade_code, period


def load_history(trade_code):
    LOG.info('[%s]' % trade_code)
    stock = db.stock_by_trade_code(trade_code)
    stock.month_history = list()
    stock.week_history = list()
    stock.day_history = list()
    stock.hour_history = list()

    for period in property.FINAM_PERIODS:
        process_by_period(stock, period)

    stock.save()
    return trade_code


def history_all_stocks():
    LOG.info("Load all stocks")
    connect()
    stocks = s.Stock.objects()
    all_stocks = stocks.count()
    for num, stock in enumerate(stocks):
        load_history(stock.trade_code)
        LOG.info("Load [%d/%d] %s" % (num, all_stocks, stock.trade_code))
    close()
    return RSP_FINAM_CODE_ALL


def loader(words):
    LOG.info('Start loading from Finam history [%s]' % " ".join(words))
    if len(words) == 1:
        return history_all_stocks()
    else:
        return load_history(trade_code=str(words[1]).upper())
