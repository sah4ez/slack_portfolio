import my_log
import loader_from_file as lfl
import re
import config

LOG = my_log.get_logger('update')


def update(words):
    num = None

    if words.__len__() > 1 and re.compile(r'[0-9]').match(words[1]):
        num = int(words[1])

    download = False
    if words.__len__() > 2:
        download = words[2] in config.CMD_DOWNLOAD_FILES

    LOG.info("Update %s files and %s download" %
             (str(num) if num is not None else 'all', str(download)))
    lfl.load_stocks(num, download)
