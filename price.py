import config
import loader_from_file


def price(words):
    company = words[1]
    print(company)
    stock = loader_from_file.load_one_stock(company)
    if stock is None:
        return format(config.RSP_NOF_FOUND_STOCK % company)
    else:
        return format(config.RSP_PRICE % (
            stock.emitent_full_name,
            stock.trade_code,
            stock.last_price))
