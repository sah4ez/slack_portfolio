import my_log
import property
import datetime as datetime
import mongo.mongo as db
import loader_from_file
import config

LOG = my_log.get_logger("Finam Loader")


def loader(words):
    trade_code = str(words[1]).upper()

    LOG.info('[%s]' % trade_code)
    stock = db.stock_by_trade_code(trade_code)
    now = datetime.datetime.now()
    history_file_name = stock.trade_code + '_' + \
                        str(now.year) + '-' + \
                        str(now.month) + '-' + \
                        str(now.day)
    url = url_download_history_stock_price(stock.trade_code, stock.finame_em, history_file_name)
    path = property.TYPE2_PATH + '/' + stock.trade_code + '/' + history_file_name + '.csv'
    LOG.info('Start loading hystory for %s from %s' % (trade_code, url))
    size_download = loader_from_file.download_file(url, path)
    LOG.info('Load %d' % size_download)
    return format(config.RSP_FINAM_CODE % (stock.trade_code, str(stock.finame_em)))


def url_download_history_stock_price(trade_code, finam_em, file_name, from_day=1, from_month=1, from_year=2010,
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
                    '&mf=' + str(from_month) + \
                    '&yf=' + str(from_year) + \
                    '&from=' + str(from_day) + '.' + str(from_month) + '.' + str(from_year) + \
                    '&dt=' + str(cur_day) + \
                    '&mt=' + str(cur_month) + \
                    '&yt=' + str(cur_year) + \
                    '&to=' + str(cur_day) + '.' + str(cur_month) + '.' + str(cur_year) + \
                    '&p=10' \
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
