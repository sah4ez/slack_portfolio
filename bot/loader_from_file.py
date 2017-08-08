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
from mongo import Stock as s, mongo as db
import finam.finam as finam

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
        return os.stat(file).st_size
    except MissingSchema:
        LOG.info(format('Not found URL %s' % url))
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


def get_stock_from_file(name, line, is_download):
    stock = s.Stock()
    stock_line(stock,line=line)
    stock.short_name = get_short_name(stock.trade_code)
    stock.finame_em = finam.code(stock.short_name)
    stock.last_price = get_last_price(stock.trade_code)
    stock.volume_stock_on_market = get_volume_stock_on_market(stock.trade_code)

    if is_download:
        download = threading.Thread(load_files(line[7], line[38]))
        download.start()
        download.join()
    stock.files_name = get_list(property.TYPE2_PATH + "/" + stock.trade_code + property.ARCHIVES + '/')
    return stock


def stock_line(stock, line):
    stock.datestamp = datetime.datetime.utcnow()
    stock.datestamp = line[0]
    stock.currency = line[14]
    stock.trade_code = line[7]
    stock.emitent_full_name = line[11]
    stock.capitalisation = float(extractor.get_value_capitalization(stock.trade_code))
    stock.free_float = float(extractor.get_free_float(stock.trade_code))
    stock.official_url = line[37]
    stock.url = line[38]
    return stock


def stock_from_line(name, line, is_download=True):
    if line[4] == property.STOCKS and name.lower() in line[11].lower():
        return get_stock_from_file(name, line, is_download)


def update_stock_from_file(name, download, is_priviledged=False):
    try:
        if name == "":
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
        action = read_to_list(property.DATA)
        stock_file = None
        for a in action:
            stock_file = stock_from_line(name, a, download)
            if stock_file is not None:
                break
        stock_file.save()


def load_one_stock(name, is_privileged=False):
    LOG.info('Load stock with name %s and privileged is %s' % (name, str(is_privileged)))
    stock = None
    try:
        stock = db.stock_by_emitet_name(name, is_privileged)
    except db.NotFoundStock:
        action = read_to_list(property.DATA)
        for a in action:
            if is_privileged:
                if re.compile(property.PRIVILEGED).match(a[7]):
                    stock = stock_from_line(name, a)
                    if stock is not None:
                        break
            else:
                stock = stock_from_line(name, a)
                if stock is not None:
                    break
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


def load_stocks(count=None, upload_files=False):
    action = read_to_list(property.DATA)
    sort_action = []
    num = 0
    for a in action:
        if a[4] == property.STOCKS:
            if count is not None and count == num:
                break
            num += 1
            trade_code = a[7]
            try:
                stock = db.stock_by_trade_code(trade_code)
            except db.NotFoundStock:
                stock = s.Stock()
            stock_line(stock, line=a)
            stock.files_name = get_list(property.TYPE2_PATH + "/" + stock.trade_code + property.ARCHIVES + '/')
            stock.short_name = get_short_name(stock.trade_code)
            stock.finame_em = finam.code(stock.short_name)

            sort_action.append(stock)
            if upload_files:
                LOG.info("Will updated finance document company %s" % stock.short_name)
                load_files(stock.trade_code, stock.url)
            LOG.info("Save stock %s" % str(stock))
            stock.save()
    LOG.info("Updated %d" % num)
    return sort_action


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
