import concurrent
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from csv import *
from datetime import datetime
from os.path import isfile, join

from selenium import webdriver

import extractor
import my_log
import property
from mongo import Stock as s, mongo as db
from resources.loader import download_file, load_files

LOG = my_log.get_logger('loader_from_file')


def load_all():
    download_file(property.URL_DATA, property.DATA)
    download_file(property.URL_DATA_DESCRIPTION, property.DATA_DESCRIPTION)
    download_file(property.URL_CAPITALIZATION, property.CAPITALIZATION)
    download_file(property.URL_FREE_FLOAT, property.FREE_FLOAT)


def read_to_list(file):
    arr = list()
    with open(file, newline='', encoding='cp1251') as csvfile:
        moex_data = reader(csvfile, dialect='excel', delimiter=';')
        for row in moex_data:
            arr.append(row)
    return arr


def finam_code(short_name):
    LOG.info('Get finame code by [%s]' % short_name)
    with (open(file='./res/finam_em.csv', mode='r')) as f:
        for line in f:
            if short_name in line.split(';')[1]:
                return line.split(';')[0]


def stock_line(stock, line):
    stock.datestamp = datetime.utcnow()
    stock.datestamp = line[0]
    stock.currency = line[14]
    stock.trade_code = line[7]
    stock.emitent_full_name = line[11]
    stock.capitalisation = float(extractor.get_value_capitalization(stock.trade_code))
    stock.free_float = float(extractor.get_free_float(stock.trade_code))
    stock.official_url = line[37]
    stock.url = line[38]
    return stock


def url_board(trade_code):
    url = property.URL_BOARD + trade_code
    download_file(url, 'res/companies/' + trade_code + '/' + property.BOARD)
    html = html_source(url)
    return html


def get_stock_from_file(line, is_download):
    stock = s.Stock()
    stock_line(stock, line=line)
    html = url_board(stock.trade_code)
    stock.short_name = get_short_name(stock.trade_code, html)
    stock.finame_em = finam_code(stock.short_name)
    stock.last_price = get_last_price(stock.trade_code)
    stock.volume_stock_on_market = get_volume_stock_on_market(stock.trade_code)
    stock.lot = extractor.get_lot(stock.trade_code, html)

    if is_download:
        download = threading.Thread(load_files(line[7], line[38]))
        download.start()
        download.join()
    stock.files_name = get_list(property.TYPE2_PATH + "/" + stock.trade_code + property.ARCHIVES + '/')
    return stock


def stock_from_line(name, line, is_download=True):
    if line[4] == property.STOCKS and name.lower() in line[11].lower():
        return get_stock_from_file(line, is_download)


def update_stock_from_file(name, download, is_priviledged=False):
    try:
        LOG.info('Update from file')
        if name == "" or name is None:
            raise db.NotFoundStock
        stock = db.stock_by_emitet_name(name, is_priviledged)
        action = read_to_list(property.DATA)
        stock_file = None
        for a in action:
            stock_file = stock_from_line(name, a, download)
            if stock_file is not None:
                break
        stock.update_file(stock_file)
        stock.save()
    except db.NotFoundStock:
        LOG.error('Not found stock. Update all.')
        load_stocks(upload_files=download)


def get_stock_from_array(name, is_privileged):
    actions = read_to_list(property.DATA)
    for action in actions:
        if is_privileged:
            if re.compile(property.PRIVILEGED).match(action[7]):
                stock = stock_from_line(name, action)
                if stock is not None:
                    return stock
        else:
            stock = stock_from_line(name, action)
            if stock is not None:
                return stock


def load_one_stock(name, is_privileged=False):
    LOG.info('Load stock with name %s and privileged is %s' % (name, str(is_privileged)))
    stock = None
    try:
        stock = db.stock_by_emitet_name(name, is_privileged)
    except db.NotFoundStock:
        stock = get_stock_from_array(name, is_privileged)

    if stock is None:
        raise db.NotFoundStock(name)
    else:
        stock.save()
    return stock


def get_stocks_contains(company):
    action = read_to_list(property.DATA)
    found = list()
    for a in action:
        if a[4] == 'Акции' and company.lower() in a[11].lower():
            found.append(a[11] + ' | ' + a[7])
    return found


def load_stocks(count=None, upload_files=False):
    action = read_to_list(property.DATA)
    sort_action = list()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_stock, a, count, num, sort_action, upload_files): (num, a)
                   for (num, a) in enumerate(action)}
        for future in concurrent.futures.as_completed(futures):
            data = futures[future]
            try:
                num = future.result()
            except Exception as exc:
                LOG.error('%r generated an exception: %s' % (data, exc))
    return sort_action


def process_stock(a, count, num, sort_action, upload_files):
    if a[4] == property.STOCKS:
        if count is not None and count == num:
            return
        trade_code = a[7]
        LOG.info('Process stock %s in thred %s' % (trade_code, threading.get_ident()))
        try:
            stock = db.stock_by_trade_code(trade_code)
        except db.NotFoundStock:
            stock = s.Stock()
        html = url_board(trade_code=stock.trade_code)
        stock_line(stock, line=a)
        stock.files_name = get_list(property.TYPE2_PATH + "/" + stock.trade_code + property.ARCHIVES + '/')
        stock.short_name = get_short_name(stock.trade_code, html)
        stock.finame_em = finam_code(stock.short_name)
        stock.lot = extractor.get_lot(stock.trade_code, html)

        sort_action.append(stock)
        if upload_files:
            LOG.info("Will updated finance document company %s" % stock.short_name)
            load_files(stock.trade_code, stock.url)
        LOG.info("Save stock %s" % str(stock))
        stock.save()
        return num


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
                last_price = line.strip().replace(',', ".").replace(' ', '')
                if last_price == '-':
                    LOG.warn("Last price is: %s" % last_price)
                    return 0
                LOG.info("Last price is: %.2f" % float(last_price))
                return float(last_price)
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


def get_short_name(code, html):
    LOG.info('Get short name %s' % code)
    found = re.compile(property.SHORT_NAME_STOCK).search(html)
    if found is not None:
        name = str(found.group(0)).replace('<th>Краткое наименование</th><td>', '').replace('</td>', '')
        return name


def html_source(url):
    driver = webdriver.PhantomJS(executable_path=property.PATH_PHANTOMJS)
    driver.get(url)
    time.sleep(5)
    html_inner = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    driver.close()
    return html_inner
