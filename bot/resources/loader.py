import re
from datetime import datetime

from pip._vendor import requests
from pip._vendor.requests.exceptions import MissingSchema
from bot.my_log import get_logger
import os

from bot.extractor import get_id_and_ext_file
from bot.property import *

LOG = get_logger("resource.loader")


def download_file(url, file):
    try:
        headers = {'User-Agent': 'curl'}
        u = requests.get(url, headers=headers)

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
    folder = TYPE2_PATH + '/' + name
    file = open(folder + '/url.txt', 'w+')
    path = folder + TYPE2
    path_file = folder.replace('company', 'files') + FILES
    file.write(url)
    download_file(url, path)
    download_file(str(url).replace('company', 'files'), path_file)
    file.close()


def download_type3(url, name):
    folder = TYPE2_PATH + '/' + name
    file = open(folder + '/url.txt', 'w+')
    path_file = folder + FILES2
    url = str(url).replace('company', 'files')
    file.write(url)
    download_file(url, path_file)
    file.close()


def download_from_disclosure(url, name):
    folder = TYPE2_PATH + '/' + name
    with open(folder + '/url.txt', 'w+') as file:
        url = str(url).replace('company', 'files')
        file.write(url)

        path_file = folder + FILES3
        download_file(url + DISCLOSURE_ALL, path_file)
        path_file = folder + FILES4
        download_file(url + DISCLOSURE_FIN, path_file)
        path_file = folder + FILES5
        download_file(url + DISCLOSURE_CONSOLIDATION_FIN, path_file)

        file.close()


def is_today(file):
    date_now = datetime.now()
    if not os.path.isfile(file):
        return False
    date_file = datetime.fromtimestamp(os.stat(file).st_ctime)
    return datetime(date_now.year, date_now.month, date_now.day) <= datetime(date_file.year, date_file.month,
                                                                             date_file.day)


def parsing_line(path, file, line):
    files = list()
    group = re.compile(DOWNLOAD_URL_DISCLOSURE)
    if (file == FILES or file == FILES2) and DOWNLOAD_URL in line:
        id, extension, = get_id_and_ext_file(line)
        download_file_path = path + ARCHIVES + '/' + id + '.' + extension
        if is_today(download_file_path):
            return
        download_file(HTTP_WWW + DOWNLOAD_URL + id, download_file_path)
        files.append(download_file_path)

    elif file in (FILES3, FILES4, FILES5) and group.findall(line):
        LOG.info("Found file: %s" % group.findall(line))
    return files


def extract_files(path, file):
    files = list()
    try:
        with open(path + file, encoding="UTF-8") as first:
            LOG.info('Extract files from: %s' % path + file)
            try:
                for line in first:
                    parsing_line(path, file, line)
            except UnicodeDecodeError:
                LOG.info('Cannot read lines in file UTF-8: %s' % (path + file))
                with open(path + file, encoding="CP1251") as second:
                    LOG.info('Open in cp-1251: %s' % (path + file))
                    for line in second:
                        parsing_line(path, file, line)
    except FileNotFoundError:
        LOG.info('Not found file %s' % (path + file))
    return files


def load_files(trade_code, link):
    files = list()
    create_path(TYPE2_PATH + '/' + trade_code)
    create_path(TYPE2_PATH + '/' + trade_code + ARCHIVES)
    download_type2(link + '&type=2', trade_code)
    files.extend(extract_files(TYPE2_PATH + '/' + trade_code, FILES))
    download_type3(link + '&type=3', trade_code)
    files.extend(extract_files(TYPE2_PATH + '/' + trade_code, FILES2))
    download_from_disclosure(link, trade_code)
    if files.__len__() == 0:
        files.extend(extract_files(TYPE2_PATH + '/' + trade_code, FILES3))
        files.extend(extract_files(TYPE2_PATH + '/' + trade_code, FILES4))
        files.extend(extract_files(TYPE2_PATH + '/' + trade_code, FILES5))


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
