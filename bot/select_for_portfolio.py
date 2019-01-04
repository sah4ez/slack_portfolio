from bot.my_log import get_logger
from bot.config import RSP_GET_LIST_SELECTED, RSP_SELECT_FOR_PORTFOLIO
from bot.property import SELECTED_STOCKS
from bot.loader_from_file import load_one_stock
from bot.parser_command.command import name_and_priviledget

LOG = get_logger("select_for_portfolio")


def save_stock(stock):
    with open(file=SELECTED_STOCKS, mode='a+', encoding='UTF-8') as file:
        string = ';'.join(get_parameters_stock(stock))
        file.write(string + '\n')
        file.flush()
        file.close()
    LOG.info("Company was added.")


def select(words):
    company, privileged = name_and_priviledget(words)
    LOG.info("Select: %s" % company)
    stock = load_one_stock(company, privileged)
    save_stock(stock)
    return get_response(stock)


def get_response(stock):
    return format(RSP_SELECT_FOR_PORTFOLIO % (stock.emitent_full_name, stock.trade_code, stock.last_price))


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
    with open(file=SELECTED_STOCKS, mode='r', encoding='UTF-8') as file:
        for num, line in enumerate(file, 1):
            selected += line.replace(';', ' | ')
            lines = num
        file.close()
    LOG.info("Found %d selected companies" % lines)
    return format(RSP_GET_LIST_SELECTED % selected)
