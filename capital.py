import config
import loader_from_file


def capital(words):
    company = words[1]
    stock = loader_from_file.load_one_stock(company)
    if stock is None:
        return format(config.RSP_NOF_FOUND_STOCK % company)
    else:
        return format(config.RSP_CAPITAL % (
            stock.emitent_full_name,
            float(stock.capitalisation),
            float(stock.volume_stock_on_market),
            float(stock.capitalisation / stock.volume_stock_on_market)
        ))
