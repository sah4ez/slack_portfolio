import my_log
import config
import property
import loader_from_file

LOG = my_log.get_logger("select_for_portfolio")


def select(words):
    company = " ".join(words[1:])
    LOG.info("Select: %s" % company)
    stock = loader_from_file.load_one_stock(company)
    with open(file=property.SELECTED_STOCS, mode='a+', encoding='UTF-8') as file:
        string = ';'.join(get_parameters_stock(stock))
        file.write(string + '\n')
        file.flush()
        selected = ''
        for line in file:
            selected += line
        file.close()
    LOG.info("Company was added.")
    return format(config.RSP_SELECT_FOR_PORTFOLIO % company) + selected


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
    with open(file=property.SELECTED_STOCS, mode='r', encoding='UTF-8') as file:
        for num, line in enumerate(file, 1):
            selected += line.replace(';', ' | ')
        file.close()
    LOG.info("Found %d selected companies")
    return format(config.RSP_GET_LIST_SELECTED % selected)
