import my_log
import loader_from_file
import config

LOG = my_log.get_logger("finder")


def find(words):
    company = " ".join(words[1:])
    LOG.info("Find companies contains '%s'" % company)
    list_found_stocks = loader_from_file.get_stocks_contains(company)
    if list_found_stocks.__len__() == 0:
        LOG.info(config.RSP_NOT_FOUND)
        return config.RSP_NOT_FOUND
    LOG.info("Found %s" % str(list_found_stocks.__len__()))
    return format(config.RSP_FIND % "\n".join(list_found_stocks))
