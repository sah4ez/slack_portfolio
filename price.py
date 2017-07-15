import config
import loader_from_file
import my_log

LOG = my_log.get_logger('price')


def price(words):
    company = " ".join(words[1:])
    # print(company)
    LOG.info(company)

    stock = loader_from_file.load_one_stock(company)
    if stock is None:
        return format(config.RSP_NOF_FOUND_STOCK % company)
    else:
        return format(config.RSP_PRICE % (
            stock.emitent_full_name,
            stock.trade_code,
            stock.last_price))
