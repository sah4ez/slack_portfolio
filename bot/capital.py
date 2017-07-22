import config
import loader_from_file


def capital(words):
    company = " ".join(words[1:])
    stock = loader_from_file.load_one_stock(company)
    return response(stock, company)


def capital_p(words):
    company = " ".join(words[1:])
    stock = loader_from_file.load_one_stock_p(company)
    return response(stock, company)


def response(stock, company):
    if stock is None:
        return format(config.RSP_NOF_FOUND_STOCK % company)
    else:
        return format(config.RSP_CAPITAL % (
            stock.emitent_full_name,
            float(stock.capitalisation),
            float(stock.volume_stock_on_market),
            float(stock.capitalisation / stock.volume_stock_on_market)
        ))
