from bot.my_log import get_logger
from bot.loader_from_file import get_stocks_contains
from bot.config import RSP_NOT_FOUND, RSP_FIND

LOG = get_logger("finder")


def find(words):
    company = " ".join(words[1:])
    LOG.info("Find companies contains '%s'" % company)
    list_found_stocks = get_stocks_contains(company)
    if list_found_stocks.__len__() == 0:
        LOG.info(RSP_NOT_FOUND)
        return RSP_NOT_FOUND
    LOG.info("Found %s" % str(list_found_stocks.__len__()))
    return format(RSP_FIND % "\n".join(list_found_stocks))
