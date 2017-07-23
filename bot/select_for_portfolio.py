import my_log
import config
import property
import loader_from_file

LOG = my_log.get_logger("select_for_portfolio")


def save_stock(stock):
    with open(file=property.SELECTED_STOCKS, mode='a+', encoding='UTF-8') as file:
        string = ';'.join(get_parameters_stock(stock))
        file.write(string + '\n')
        file.flush()
        file.close()
    LOG.info("Company was added.")


def select(words):
    company = " ".join(words[1:])
    LOG.info("Select: %s" % company)
    stock = loader_from_file.load_one_stock(company)
    save_stock(stock)
    return get_response(stock)


def select_p(words):
    company = " ".join(words[1:])
    LOG.info("Select: %s" % company)
    stock = loader_from_file.load_one_stock_p(company)
    save_stock(stock)
    return get_response(stock)


def get_response(stock):
    return format(config.RSP_SELECT_FOR_PORTFOLIO % (stock.emitent_full_name, stock.trade_code, stock.last_price))


def get_parameters_stock(stock):
    parameter = list()
    parameter.append(stock.emitent_full_name)
    parameter.append(stock.trade_code)
    parameter.append(str(stock.last_price))
    parameter.append(str(stock.volume_stock_on_market))
    parameter.append(str(stock.capitalisation))
    parameter.append(str(stock.capitalisation / stock.volume_stock_on_market))
    return parameter


def get_list_selected():
    selected = 'Name | Trade Code | Price | Volume | Capitalization | Cap/Volume \n'
    LOG.info("Get list selected companies")
    lines = 0
    with open(file=property.SELECTED_STOCKS, mode='r', encoding='UTF-8') as file:
        for num, line in enumerate(file, 1):
            selected += line.replace(';', ' | ')
            lines = num
        file.close()
    LOG.info("Found %d selected companies" % lines)
    return format(config.RSP_GET_LIST_SELECTED % selected)
