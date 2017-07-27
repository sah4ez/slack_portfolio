import my_log
import loader_from_file as lfl
import re
import config
import parser_command.command as p

LOG = my_log.get_logger('update')


def update(words):
    num = None
    download = False

    company, privileged = p.name_and_priviledget(words)

    count_words = words.__len__()
    if count_words > 1:
        if re.compile(r'[0-9]').match(words[1]):
            num = int(words[1])
        elif words[count_words - 1] in config.CMD_DOWNLOAD_FILES:
            company = ' '.join(words[1:count_words - 1])
            download = True
        else:
            company = ' '.join(words[1:count_words])

    LOG.info("Update %s files and %s download" %
             (str(num) if num is not None else company, str(download)))
    if company is None:
        lfl.load_stocks(num, download)
    else:
        lfl.update_stock_from_file(company, download, privileged)


def update_metainfo():
    lfl.load_all()
    return config.RSP_UPDATE_METAINFO
