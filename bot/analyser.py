import re
import my_log
import mongo.mongo as db
import property
import numpy as np

LOG = my_log.get_logger("analyzer")


def analyse(words):
    LOG.info("Start analyse portfolio [%s]" % " ".join(words[1:]))
    companies = list()
    count = None
    size = words.__len__()
    if size >= 3:
        count, to = get_count(size, words)
        companies = all_stock(words[1:to])
    elif size == 2:
        count, to = get_count(size, words)
        if to != size:
            companies = stocks_from_file()
        else:
            companies = all_stock(words[1:to])
    else:
        companies = stocks_from_file()
    return response(companies, count)


def get_count(to, words):
    if re.compile(r'[0-9]').match(words[to - 1]):
        return words[to - 1], to - 1
    return None, to


def all_stock(stocks):
    companies = list()
    for trade_code in stocks:
        companies.append(db.stock_by_trade_code(trade_code))
    return companies


def stocks_from_file():
    companies = list()
    with open(property.SELECTED_STOCKS, mode='r', encoding='UTF-8') as file:
        for line in file:
            trade_code = line.split(';')[1]
            companies.append(db.stock_by_trade_code(trade_code))
    return companies


def response(companies, count):
    header = "Trade code | Risk | Income \n"
    lines = list()
    pattern = "%s | %.2f%% | %.2f%%"
    risks = []
    incomes = []
    for company in companies:
        if count is None:
            count = company.month_history.__len__()

        risk_by_one = risk(company, count)
        income_by_one = income(company, count)
        risks.append(risk_by_one)
        incomes.append(income_by_one)
        lines.append(format(pattern % (company.trade_code, risk_by_one, income_by_one)))
    part = np.ndarray([companies.__len__()])
    for i in part:
        i = 1 / companies.__len__()

    covariance_m = covariance_matrix(companies, count)
    print(np.sqrt(
        np.multiply(np.multiply(np.asscalar(covariance_m),
                                          np.asscalar(part)),
                              np.asscalar(part))))

    return header + "\n".join(lines)


def income(stock, count):
    return np.mean(income_by_item(stock, count))


def risk(stock, count):
    return np.std(income_by_item(stock, count))


def covariance_matrix(stocks, count):
    incomes = []
    for stock in stocks:
        incomes.append(income_by_item(stock, count))
    c = np.vstack(incomes)
    covar_matrix = np.corrcoef(c)
    return covar_matrix


def income_by_item(stock, count):
    percent_by_item = list()
    prev = None
    for price in stock.month_history[int(stock.month_history.__len__() - int(count)):]:
        if prev is not None:
            percent_by_item.append(percent(prev, price.value))
        prev = price.value
    return percent_by_item


def percent(x, y):
    return (y * 100.0) / x - 100
