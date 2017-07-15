import config
import parser
import loader_from_file


def capital(command):
    company = parser.company_capital(command)
    stock = loader_from_file.load_one_stock(company)
    if stock is None:
        return format("Акция не найдена %s" % company)
    else:
        return format(config.RSP_CAPITAL % (company, stock))
