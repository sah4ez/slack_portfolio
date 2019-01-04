from bot.my_log import get_logger
from bot.loader_from_file import update_stock_from_file, load_stocks, load_all
import re
from bot.config import RSP_UPDATE_METAINFO, CMD_DOWNLOAD_FILES
from bot.parser_command.command import name_and_priviledget

LOG = get_logger('update')


def update(words):
    num = None
    download = False

    company, privileged = name_and_priviledget(words)

    count_words = words.__len__()
    if count_words > 1:
        if re.compile(r'[0-9]+').match(words[1]):
            num = int(words[1])
        elif words[count_words - 1] in CMD_DOWNLOAD_FILES:
            company = ' '.join(words[1:count_words - 1])
            download = True
        else:
            company = ' '.join(words[1:count_words])

    LOG.info("Update %s files and %s download" % (str(num) if num is not None else company, str(download)))
    if company is None or len(company) == 0:
        load_stocks(num, download)
    else:
        update_stock_from_file(company, download, privileged)


def update_metainfo():
    load_all()
    return RSP_UPDATE_METAINFO
