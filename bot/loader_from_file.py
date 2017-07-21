import os
import re
import threading
import time
from csv import *
from datetime import datetime
from os.path import isfile, join

from pip._vendor import requests
from pip._vendor.requests.exceptions import MissingSchema
from selenium import webdriver

import extractor
import my_log
import property
from Stock import Stock
import mongo.Stock as s
import mongo.mongo as db

# from ..database import db_helper

LOG = my_log.get_logger('loader_from_file')


def download_file(url, file):
    try:
        u = requests.get(url=url)

        with open(file=file, mode='wb') as f:
            for chunk in u.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        f.close()
        LOG.info(format('Load from %s file %s' % (url, file)))
    except MissingSchema:
        LOG.info(format('Not found URL %s' % url))
        # print('Not found URL %s' % url)
    except requests.exceptions.SSLError:
        LOG.info('Bad SLL of url: %s' % url)


def download_type2(url, name):
    folder = property.TYPE2_PATH + '/' + name
    file = open(folder + '/url.txt', 'w+')
    path = folder + property.TYPE2
    path_file = folder.replace('company', 'files') + property.FILES
    file.write(url)
    download_file(url, path)
    download_file(str(url).replace('company', 'files'), path_file)
    file.close()


def download_type3(url, name):
    folder = property.TYPE2_PATH + '/' + name
    file = open(folder + '/url.txt', 'w+')
    path_file = folder + property.FILES2
    url = str(url).replace('company', 'files')
    file.write(url)
    download_file(url, path_file)
    file.close()


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def load_all():
    download_file(property.URL_DATA, property.DATA)
    download_file(property.URL_DATA_DESCRIPTION, property.DATA_DESCRIPTION)
    download_file(property.URL_CAPITALIZATION, property.CAPITALIZATION)
    download_file(property.URL_FREE_FLOAT, property.FREE_FLOAT)


def read_to_list(file):
    arr = []

    with open(file, newline='', encoding='cp1251') as csvfile:
        moex_data = reader(csvfile, dialect='excel', delimiter=';')
        for row in moex_data:
            arr.append(row)
    return arr


def get_stock(name, line):
    stock = Stock()
    stock.stock_line(line=line)
    # stock.finame_em = get_finam_code(stock.short_name)
    if name.lower() in stock.emitent_full_name.lower():
        stock.short_name = get_short_name(stock.trade_code)
        stock.last_price = get_last_price(stock.trade_code)
        stock.volume_stock_on_market = get_volume_stock_on_market(stock.trade_code)

        download = threading.Thread(load_files(line[7], line[38]))
        download.start()
        download.join()
        stock.files_name = get_list(property.TYPE2_PATH + "/" + stock.trade_code + property.ARCHIVES + '/')
        return stock
    return None


def load_one_stock(name):
    action = read_to_list(property.DATA)
    stock = None
    for a in action:
        if a[4] == 'Акции' and name.lower() in a[11].lower():
            stock = get_stock(name, a)
    return stock


def load_one_stock_p(name):
    action = read_to_list(property.DATA)
    for a in action:
        if a[4] == 'Акции' and name.lower() in a[11].lower() and re.compile(property.PRIVELEDGED).match(a[7]):
            return get_stock(name, a)
    return None


def get_stocks_contains(company):
    action = read_to_list(property.DATA)
    found = list()
    for a in action:
        if a[4] == 'Акции' and company.lower() in a[11].lower():
            found.append(a[11] + ' | ' + a[7])
    return found


def is_today(file):
    date_now = datetime.now()
    if not os.path.isfile(file):
        return False
    date_file = datetime.fromtimestamp(os.stat(file).st_ctime)
    return datetime(date_now.year, date_now.month, date_now.day) <= datetime(date_file.year, date_file.month,
                                                                             date_file.day)


def download_from_disclosure(url, name):
    folder = property.TYPE2_PATH + '/' + name
    file = open(folder + '/url.txt', 'w+')
    url = str(url).replace('company', 'files')
    file.write(url)

    path_file = folder + property.FILES3
    download_file(url + property.DISCLOSURE_ALL, path_file)
    path_file = folder + property.FILES4
    download_file(url + property.DISCLOSURE_FIN, path_file)
    path_file = folder + property.FILES5
    download_file(url + property.DISCLOSURE_CONSOLIDATION_FIN, path_file)

    file.close()


def load_files(trade_code, link):
    files = list()
    create_path(property.TYPE2_PATH + '/' + trade_code)
    create_path(property.TYPE2_PATH + '/' + trade_code + property.ARCHIVES)
    download_type2(link + '&type=2', trade_code)
    files.extend(extractor.extract_files(property.TYPE2_PATH + '/' + trade_code, property.FILES))
    download_type3(link + '&type=3', trade_code)
    files.extend(extractor.extract_files(property.TYPE2_PATH + '/' + trade_code, property.FILES2))
    download_from_disclosure(link, trade_code)
    if files.__len__() == 0:
        files.extend(extractor.extract_files(property.TYPE2_PATH + '/' + trade_code, property.FILES3))
        files.extend(extractor.extract_files(property.TYPE2_PATH + '/' + trade_code, property.FILES4))
        files.extend(extractor.extract_files(property.TYPE2_PATH + '/' + trade_code, property.FILES5))


def load_stocks(count):
    action = read_to_list(property.DATA)
    sort_action = []
    num = 0
    for a in action:
        if a[4] == 'Акции':
            if count is not None and count == num:
                break
            num += 1
            trade_code = a[7]
            stocks = db.contains(trade_code)

            if stocks.count() == 0:
                stock = s.Stock()
            elif stocks.count() == 1:
                stock = stocks.first()
            else:
                LOG.error("Collection contains %d the same document" % stocks.count())
                return

            # stock = s.Stock()
            stock.stock_line(line=a)

            stock.files_name = get_list(property.TYPE2_PATH + "/" + stock.trade_code + property.ARCHIVES + '/')

            stock.short_name = get_short_name(stock.trade_code)
            stock.finame_em = get_finam_code(stock.short_name)

            sort_action.append(stock)
            # db_helper.add_stock(stock)
            load_files(stock.trade_code, stock.url)
            LOG.info("Save stock %s" % str(s))
            stock.save()
    LOG.info("Updated %d" % num)
    return sort_action


# def update_history_stocks():
#     action = db_helper.get_stocks()
#     now = datetime.now()
#     for stock in action:
#         history_file_name = stock.trade_code + '_' + \
#                             str(now.year) + '-' + \
#                             str(now.month) + '-' + \
#                             str(now.day)
#         url = url_download_history_stock_price(stock.trade_code, stock.finame_em, history_file_name)
#         path = TYPE2_PATH + '/' + stock.trade_code + '/' + history_file_name + '.csv'
#         print('URL: %s' % url)
#         download_file(url, path)
#
#     return action.__sizeof__()


def get_list(path):
    only_files = ""
    if os.path.isdir(path):
        only_files = [f for f in os.listdir(path) if isfile(join(path, f)) and str(f).__getitem__(0) != '.']
    return list(only_files)


def get_last_price(trade_code):
    directory = property.TYPE2_PATH + '/' + trade_code + '/'
    file = directory + property.BOARD
    fine_line = -1
    with open(file=file, mode="rb") as f:
        LOG.info('Open file:  %s' % file)
        for num, line in enumerate(f, 1):
            line = str(line, "UTF-8")
            if property.LAST_PRICE in line:
                LOG.info("Found last price")
                fine_line = num + 3
            if fine_line == num:
                last_price = float(line.strip().replace(',', ".").replace(' ', ''))
                LOG.info("Last price is: %.2f" % last_price)
                return last_price
    f.close()
    return 0.0


def get_volume_stock_on_market(trade_code):
    directory = property.TYPE2_PATH + '/' + trade_code + '/'
    file = directory + property.BOARD
    result = 0
    with open(file=file, mode="rb") as f:
        for num, line in enumerate(f, 1):
            line = str(line, "UTF-8")
            if property.VOLUME_ON_MARKET in line:
                index = line.index(property.VOLUME_ON_MARKET)
                substring = line[index + property.VOLUME_ON_MARKET.__len__() + 9:]
                end = substring.index("</td>")
                volume = substring[:end]
                result = int(volume.replace(' ', '').strip())
                LOG.info(format("volume stock on market %d" % result))

    return result


def get_short_name(code):
    directory = property.TYPE2_PATH + '/' + code + '/'
    file = directory + property.BOARD
    create_path(directory)
    url = url_board(trade_code=code)
    html = html_source(url)
    with open(file=file, mode="w+") as f:
        try:
            name = extractor.short_name_code(html)
        except ValueError:
            time.sleep(3)
            html = html_source(url)
            try:
                name = extractor.short_name_code(html)
            except ValueError:
                name = ''
        # f.write(bytearray(html, 'UTF-8'))
        f.write(html)
        f.flush()
    f.close()
    return name


def url_board(trade_code):
    return property.URL_BOARD + trade_code


def html_source(url):
    driver = webdriver.PhantomJS(executable_path=property.PATH_PHANTOMJS)
    driver.get(url)
    time.sleep(5)
    html_inner = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    # html_inner = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
    driver.close()
    return html_inner


def get_finam_code(short_name):
    with (open(file='./res/finam_em.csv', mode='rb')) as f:
        for r in f:
            line = str(r, 'UTF-8').split(';')
            if short_name in line[1]:
                return line[0]


def url_download_history_stock_price(trade_code, finam_em, file_name, from_day=1, from_month=1, from_year=2000,
                                     extention='.csv'):
    now = datetime.now()
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
