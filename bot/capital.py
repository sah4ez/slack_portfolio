from bot.config import RSP_CAPITAL, RSP_NOF_FOUND_STOCK
import bot.loader_from_file as loader_from_file
import bot.parser_command.command as p
from bot.my_log import get_logger

LOG = get_logger('capital')


def capital(words):
    name, privileged = p.name_and_priviledget(words)
    LOG.info('Get capital for [%s, %s]' % (name, str(privileged)))

    stock = loader_from_file.load_one_stock(name, privileged)

    if stock is None:
        return format(RSP_NOF_FOUND_STOCK % name)
    else:
        return format(RSP_CAPITAL % (
            stock.emitent_full_name,
            float(stock.capitalisation),
            float(stock.volume_stock_on_market),
            float(stock.capitalisation / stock.volume_stock_on_market)
        ))
