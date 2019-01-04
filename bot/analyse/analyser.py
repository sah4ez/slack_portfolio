import re
from bot.my_log import get_logger
import bot.mongo.mongo as db
from bot.property import FINAM_PERIODS, FINAM_P_DAY, FINAM_P_WEEK, FINAM_P_HOUR, SELECTED_STOCKS, FINAM_P_MONTH
import numpy as np
import texttable as tt

LOG = get_logger("analyzer")
np.set_printoptions(formatter={'float': '{: 0.4f}'.format})


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
    if re.compile(r'[0-9]+').match(words[to - 1]):
        return words[to - 1], to - 1
    return None, to


def all_stock(stocks):
    companies = list()
    for trade_code in stocks:
        companies.append(db.stock_by_trade_code(trade_code))
    return companies


def stocks_from_file():
    companies = list()
    with open(SELECTED_STOCKS, mode='r', encoding='UTF-8') as file:
        for line in file:
            trade_code = line.split(';')[1]
            companies.append(db.stock_by_trade_code(trade_code))
    return companies


def response(companies, count):
    header = ['Trade code',
              ' R_M ', ' I_M ',
              ' R_W ', ' I_W ',
              ' R_D ', ' I_D ',
              ' R_H ', ' I_H ']
    count_column = header.__len__()
    formatter = tt.Texttable(max_width=240)
    formatter.add_row(header)
    lines = list()
    risks = {
        FINAM_P_MONTH: list(),
        FINAM_P_WEEK: list(),
        FINAM_P_DAY: list(),
        FINAM_P_HOUR: list(),
    }
    incomes = {
        FINAM_P_MONTH: list(),
        FINAM_P_WEEK: list(),
        FINAM_P_DAY: list(),
        FINAM_P_HOUR: list(),
    }
    for company in companies:
        if count is None:
            count = company.month_history.__len__()
            line = calculate_stock(company, count, risks, incomes)
        if line.__len__() == count_column:
            lines.append(line)

    lines.sort(key=lambda x: x[count_column - 1])

    risk_periods = []
    incomes_periods = []
    try:
        for period in FINAM_PERIODS:
            covariance_m = covariance_matrix(companies, count, period)
            part, t_part = get_parts(companies)
            m_c_p = mmult(companies.__len__(), covariance_m, part)
            m_c_p_t = mmult(1, m_c_p, t_part)
            risk_periods.append(format('%.3f' % np.sqrt(m_c_p_t[0][0])))
            incomes_periods.append(format('%.3f' % get_all_incomes(incomes[period], part)))
    except ValueError:
        LOG.warn('ValueError in covariance matrix')
        risk_periods = [0, 0, 0, 0]
        incomes_periods = [0, 0, 0, 0]
    for line in lines:
        formatter.add_row(line)
    amount = ['Amount']
    for num, risk_p in enumerate(risk_periods):
        amount.append(risk_p)
        amount.append(incomes_periods[num])

    formatter.add_row(amount)
    return formatter.draw()


def calculate_stock(company, count, risks, incomes):
    line = [company.trade_code]
    for period in FINAM_PERIODS:
        risk_by_one = risk(count, history_by_period(period, company))
        income_by_one = income(count, history_by_period(period, company))
        risks[period].append(risk_by_one)
        incomes[period].append(income_by_one)
        if not re.compile(r'[0-9.-]+').match(str(risk_by_one)) or \
                not re.compile(r'[0-9.-]+').match(str(income_by_one)):
            continue
        line.append(format('%.4f' % risk_by_one))
        line.append(format('%.4f' % income_by_one))
        return line


def get_all_incomes(incomes, part):
    sum_i = 0
    for i, income in enumerate(incomes):
        sum_i += income * part[0][i]
    return sum_i


def mmult(size, left, right):
    m_c_p = np.ndarray((1, size))
    for i, el in enumerate(left):
        sum_line = 0
        for j in el:
            sum_line += j * right[0][i]
        m_c_p[0][i] = sum_line
    return m_c_p


def get_parts(companies):
    count = companies.__len__()
    part = np.ndarray((1, count))
    t_part = np.ndarray((count, 1))
    for i in range(count):
        part[0][i] = 1 / count
        t_part[i][0] = 1 / count
    return part, t_part


def income(count, history):
    return np.mean(income_by_item(count, history))


def risk(count, history):
    return np.std(income_by_item(count, history))


def covariance_matrix(stocks, count, period):
    incomes = []
    for stock in stocks:
        incomes.append(income_by_item(count, history_by_period(period, stock)))
    c = np.vstack(incomes)
    covariance = np.ma.cov(c)
    if stocks.__len__() == 1:
        covariance = [[covariance]]
    return covariance


def history_by_period(period, stock):
    if period == FINAM_P_MONTH:
        return stock.month_history
    elif period == FINAM_P_WEEK:
        return stock.week_history
    elif period == FINAM_P_DAY:
        return stock.day_history
    elif period == FINAM_P_HOUR:
        return stock.hour_history


def income_by_item(count, history):
    percent_by_item = list()
    prev = None
    for price in history[int(history.__len__() - int(count)):]:
        if prev is not None:
            percent_by_item.append(percent(prev, price.value))
        prev = price.value
    return percent_by_item


def percent(x, y):
    return (y * 100.0) / x - 100
