import yahoo_finance as yf
import my_log
import mongo.mongo as db
import config
import re
import property

LOG = my_log.get_logger('yahoo.price')


def price(words):
    LOG.info('get price for [%s]' % words)
    name = " ".join(words[1:])

    if re.compile(property.PRIVILEGED_CMD).match(words[0]):
        stock = db.stock_by_emitet_name(name, is_privileged=True)
    else:
        stock = db.stock_by_emitet_name(name)

    shape = yf.Share(stock.shape())
    if shape.get_name() is None:
        return format(config.RSP_NOF_FOUND_STOCK % name)
    else:
        return format(config.RSP_PRICE % (
            stock.emitent_full_name,
            stock.trade_code,
            float(shape.get_price())))

