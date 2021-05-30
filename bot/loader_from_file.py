import concurrent
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from csv import *
import traceback
from datetime import datetime
from os.path import isfile, join

from selenium import webdriver

from bot.extractor import get_free_float, get_value_capitalization
from bot.my_log import get_logger
import bot.property as property
from bot.mongo import Stock as s, mongo as db
from bot.resources.loader import download_file, load_files

LOG = get_logger('loader_from_file')


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


def get_lot(ticker: str) -> int:
    LOG.info('Get lot size name by [%s]' % ticker)
    codes = {}
    with (open(file='./bot/res/moex_lot_size.csv', mode='r')) as f:
        for line in f:
            parts = line.split(';')
            codes[parts[0].strip()] = parts[1].strip()
    return int(codes[ticker])


def get_short_name(ticker: str) -> str:
    LOG.info('Get short name by [%s]' % ticker)
    codes = {}
    with (open(file='./bot/res/moex_short.csv', mode='r')) as f:
        for line in f:
            parts = line.split(';')
            codes[parts[0].strip()] = parts[1].strip()
    return codes[ticker]

def finam_code(ticker: str) -> str:
    LOG.info('Get finame code by [%s]' % ticker)
    codes = {}
    with (open(file='./bot/res/moex_short.csv', mode='r')) as f:
        for line in f:
            parts = line.split(';')
            codes[parts[0].strip()] = parts[1].strip()

    finam_id = {}
    with (open(file='./bot/res/finam_em.csv', mode='r')) as f:
        for line in f:
            parts = line.split(';')
            finam_id[parts[1].strip()] = parts[0].strip()

    return finam_id[codes[ticker]]


def stock_line(stock, line):
    stock.datestamp = datetime.utcnow()
    stock.datestamp = line[0]
    stock.currency = line[14]
    stock.trade_code = line[7]
    stock.emitent_full_name = line[11]
    #  stock.capitalisation = float(get_value_capitalization(stock.trade_code))
    #  stock.free_float = float(get_free_float(stock.trade_code))
    #  stock.official_url = line[37]
    #  stock.url = line[38]
    return stock


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_stock_from_file(line, is_download):
    stock = s.Stock()
    stock_line(stock, line=line)
    stock.short_name = get_short_name(stock.trade_code)
    stock.finame_em = finam_code(stock.trade_code)
    stock.last_price = get_last_price(stock.trade_code)
    stock.volume_stock_on_market = get_volume_stock_on_market(stock.trade_code)
    stock.lot = get_lot(stock.trade_code)

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
        stock = db.stock_by_trade_code(name, is_priviledged)
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
                traceback.print_exc()
    return sort_action

def load_stocks_tinvest(stocks):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_stock_tivest, num, ta): (num, ta)
                   for (num, ta) in enumerate(stocks)}
        for future in concurrent.futures.as_completed(futures):
            data = futures[future]
            try:
                num = future.result()
                print("done:", num)
            except Exception as exc:
                LOG.error('%r generated an exception: %s' % (data, exc))
                traceback.print_exc()

def process_stock_tivest(num, ta):
    trade_code = ta.ticker
    LOG.info('Process stock %s in thread %s' % (trade_code, threading.get_ident()))
    try:
        stock = db.stock_by_trade_code(trade_code)
    except db.NotFoundStock as e:
        stock = s.Stock()

    stock.update_from_tinvest(ta)
    stock.save()
    LOG.info("Save stock %s" % str(stock._id))
    return num


def process_stock(a, count, num, sort_action, upload_files):
    if a[4] == property.STOCKS:
        if count is not None and count == num:
            return
        trade_code = a[7]
        LOG.info('Process stock %s in thred %s' % (trade_code, threading.get_ident()))
        try:
            stock = db.stock_by_trade_code(trade_code)
        except db.NotFoundStock as e:
            stock = s.Stock()
        stock_line(stock, line=a)
        ## TODO: need to add loading history of the stock

        #  LOG.info("Will updated finance document company " + str(a))
        #  load_files(stock.trade_code, stock.url)
        #  stock.files_name = get_list(property.TYPE2_PATH + "/" + stock.trade_code + property.ARCHIVES + '/')
        stock.short_name = get_short_name(stock.trade_code)

        stock.finame_em = finam_code(stock.trade_code)
        #  update_stock_from_file(stock.emitent_full_name, False)
        stock.lot = get_lot(stock.trade_code)

        sort_action.append(stock)
        #  if upload_files:
        stock.save()
        LOG.info("Save stock %s" % str(stock._id))
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
