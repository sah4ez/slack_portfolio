import loader_from_file
import my_log
from property import *
import re

LOG = my_log.get_logger("extractor")


def get_value_capitalization(trade_code):
    with open(CAPITALIZATION) as f:
        next = 0
        r = '0.0'
        contain = False
        for line in f:
            if trade_code in line:
                contain = True
            if contain:
                next += 1
            if next == 7:
                r = ''.join(filter(lambda x: x.isdigit() or x == ',', line))
        if r == '':
            return '0.0'
        return (r.replace(',', '.'), '0.0')[r is None or type(r) is None]


def get_free_float(short_name):
    with open(FREE_FLOAT) as f:
        next = 0
        r = '0.0'
        contain = False
        for line in f:
            if short_name in line:
                contain = True
            if contain:
                next += 1
            if next == 3:
                r = ''.join(filter(lambda x: x.isdigit(), line))
        if r == '':
            return 0.0
        return (r.replace(',', '.'), '0.0')[r is None or type(r) is None]


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


def parsing_line(path, file, line):
    files = list()
    group = re.compile(DOWNLOAD_URL_DISCLOSURE)
    if (file == FILES or file == FILES2) and DOWNLOAD_URL in line:
        id, extension, = get_id_and_ext_file(line)
        download_file = path + ARCHIVES + '/' + id + '.' + extension
        if loader_from_file.is_today(download_file):
            return
        loader_from_file.download_file(HTTP_WWW + DOWNLOAD_URL + id, download_file)
        files.append(download_file)

    elif file in (FILES3, FILES4, FILES5) and group.findall(line):
        LOG.info("Found file: %s" % group.findall(line))
    return files


def get_id_and_ext_file(line):
    pos = str(line).index(DOWNLOAD_URL) + DOWNLOAD_URL.__len__()
    id_file = ''
    while line[pos] != '"':
        id_file += line[pos]
        pos += 1

    if id_file == '':
        RuntimeError()
    else:
        return id_file, get_extension_file(line, pos)


def get_extension_file(line, pos):
    ext = ''
    pos += 2
    while line[pos] != ',':
        ext += line[pos]
        pos += 1
    if ext == '':
        RuntimeError()
    else:
        return ext


def short_name_code(html):
    pos = str(html).index(SHORT_NAME_ATTR) + SHORT_NAME_ATTR.__len__()
    pos += 9
    name = ''
    while html[pos] != "<":
        name += html[pos]
        pos += 1
    if name == '':
        RuntimeError()
    else:
        return name


def get_lot(trade_code, source):
    try:
        if re.compile(LOT_STOCK).search(source):
            found_pattern = re.compile(LOT_STOCK).search(source).group(0)
            lot = int(re.compile(r'[0-9]+').search(found_pattern.replace(' ', '')).group(0))
            LOG.info('Found lot value %d for stock %s' % (lot, trade_code))
            return lot
    except FileNotFoundError:
        LOG.error('Not found file %s for stock %s' % (source, trade_code))

    return 0
