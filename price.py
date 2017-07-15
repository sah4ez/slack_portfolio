import config
import loader_from_file
import parser


def price(command):
    company = parser.company_price(command)
    print(company)
    stock = loader_from_file.load_one_stock(company)
    if stock is not None:
        return format(config.RSP_PRICE % (stock.emitent_full_name, stock.trade_code, stock.last_price))
    else:
        return format("Не найдена акция для %s" % company)
