import yahoo_finance as yf
from bot.my_log import get_logger
import bot.mongo.mongo as db
from bot.config import RSP_PRICE, RSP_NOF_FOUND_STOCK
from bot.parser_command.command import name_and_priviledget

LOG = get_logger('yahoo.price')


def price(words):
    LOG.info('Get price for [%s]' % words)
    name, privileged = name_and_priviledget(words)

    stock = db.stock_by_emitet_name(name, is_privileged=privileged)

    shape = yf.Share(stock.shape())
    if shape.get_name() is None:
        return format(RSP_NOF_FOUND_STOCK % name)
    else:
        return format(RSP_PRICE % (
            stock.emitent_full_name,
            stock.trade_code,
            float(shape.get_price())))
