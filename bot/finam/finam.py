import my_log
import property
import datetime as datetime
import mongo.mongo as db
import loader_from_file
import config
import mongo.Price as p
import mongo.Stock as s
import time

LOG = my_log.get_logger("Finam Loader")

periods = [property.FINAM_P_MONTH, property.FINAM_P_WEEK, property.FINAM_P_DAY, property.FINAM_P_HOUR]


def loader(words):
    LOG.info('Start loading from Finam history [%s]' % " ".join(words))
    count = None
    if words.__len__() == 3:
        count = words[2]
    if words[1] in config.ARG_FINAM_CODE_ALL:
        return history_all_stocks(count) if count is not None else history_all_stocks()
    else:
        trade_code = str(words[1]).upper()
        return load_history(trade_code, count) if count is not None else load_history(trade_code)


def history_all_stocks(count=None):
    LOG.info("Load all stocks")
    stocks = s.Stock.objects()
    for num, stock in enumerate(stocks):
        LOG.info("Load [%d/%d] %s" % (num, stocks.count(), stock.trade_code))
        load_history(stock.trade_code, count)
    return config.RSP_FINAM_CODE_ALL


def save_to_db(stock, path, count, period):
    LOG.info("Save history %s to DB" % stock.trade_code)
    with open(file=path, mode='r', encoding='UTF-8') as file:
        try:
            for num, line in enumerate(file):
                if num == 0:
                    continue
                words = line.split(",")
                date = words[2] + ' ' + words[3]
                value = words[7]
                date_time = datetime.datetime.strptime(date, '%d/%m/%y %H:%M:%S')
                price = p.Price()
                price.value = float(value)
                price.date = date_time
                set_price(stock, price, period)
        except UnicodeDecodeError:
            LOG.error('Bad file %s' % path)
        finally:
            file.close()


def set_price(stock, price, period):
    if period == property.FINAM_P_MONTH:
        stock.month_history.append(price)
    elif period == property.FINAM_P_WEEK:
        stock.week_history.append(price)
    elif period == property.FINAM_P_DAY:
        stock.day_history.append(price)
    elif period == property.FINAM_P_HOUR:
        stock.hour_history.append(price)


def load_history(trade_code, count=None):
    LOG.info('[%s]' % trade_code)
    stock = db.stock_by_trade_code(trade_code)
    stock.month_history = list()
    stock.week_history = list()
    stock.day_history = list()
    stock.hour_history = list()
    now = datetime.datetime.now()

    for period in periods:
        history_file_name = stock.trade_code + '_' + \
                            str(now.year) + '-' + \
                            str(now.month) + '-' + \
                            str(now.day) + '-' + period
        if period == property.FINAM_P_WEEK:
            date_from = datetime.datetime.now() - datetime.timedelta(days=property.FINAM_SHIFT_WEEK)
        elif period == property.FINAM_P_DAY:
            date_from = datetime.datetime.now() - datetime.timedelta(days=property.FINAM_SHIFT_DAY)
        elif period == property.FINAM_P_HOUR:
            date_from = datetime.datetime.now() - datetime.timedelta(hours=property.FINAM_SHIFT_HOUR)
        else:
            date_from = datetime.datetime.now() - datetime.timedelta(days=property.FINAM_SHIFT_MONTH)

        url = url_download_history_stock_price(stock.trade_code,
                                               stock.finame_em,
                                               history_file_name,
                                               period=period,
                                               from_day=date_from.day,
                                               from_month=date_from.month,
                                               from_year=date_from.year)
        path = property.TYPE2_PATH + '/' + stock.trade_code + '/' + history_file_name + '.csv'
        LOG.info('Start loading hystory for %s from %s' % (trade_code, url))
        size_download = loader_from_file.download_file(url, path) / 1024
        LOG.info('Load %.2f Кб' % size_download)
        save_to_db(stock, path, count, period)

    stock.save()
    return format(config.RSP_FINAM_CODE % (stock.trade_code, str(stock.finame_em)))


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


def code(short_name):
    LOG.info('Get finame code by [%s]' % short_name)
    with (open(file='./res/finam_em.csv', mode='rb')) as f:
        for r in f:
            line = str(r, 'UTF-8').split(';')
            if short_name in line[1]:
                return line[0]
