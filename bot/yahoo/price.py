import yahoo_finance as yf
import my_log
import mongo.mongo as db
import config
import parser_command.command as p

LOG = my_log.get_logger('yahoo.price')


def price(words):
    LOG.info('Get price for [%s]' % words)
    name, privileged = p.name_and_priviledget(words)

    stock = db.stock_by_emitet_name(name, is_privileged=privileged)

    shape = yf.Share(stock.shape())
    if shape.get_name() is None:
        return format(config.RSP_NOF_FOUND_STOCK % name)
    else:
        return format(config.RSP_PRICE % (
            stock.emitent_full_name,
            stock.trade_code,
            float(shape.get_price())))
