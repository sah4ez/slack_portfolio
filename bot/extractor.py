import loader_from_file
import my_log
from property import *

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
        with open(path + file) as f:
            LOG.info('Extract files from: %s' % path + file)
            try:
                for line in f:
                    if DOWNLOAD_URL in line:
                        id, extension, = get_id_and_ext_file(line)
                        download_file = path + ARCHIVES + '/' + id + '.' + extension
                        if loader_from_file.is_today(download_file):
                            return
                        loader_from_file.download_file(HTTP_WWW + DOWNLOAD_URL + id, download_file)
                        files.append(download_file)
                return files
            except UnicodeDecodeError:
                LOG.info('Cannot read lines in file: %s' % (path + file))
    except FileNotFoundError:
        LOG.info('Not found file %s' % (path + file))


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
