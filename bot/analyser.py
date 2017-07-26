import re
import my_log
import mongo.mongo as db
import property
import numpy as np

LOG = my_log.get_logger("analyzer")
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
    header = "Short Name| Trade code | Risk_M | Income_M | " + \
             "Risk_W | Income_W | Risk_D | Income_D | Risk_H | Income_H |  \n"
    lines_pattern = list()
    lines = list()
    pattern = "%s | %s | %.2f%% | %.2f%% | %.2f%% | %.2f%% | %.2f%% | %.2f%% | %.2f%% | %.2f%% "
    risks = {
        property.FINAM_P_MONTH: list(),
        property.FINAM_P_WEEK: list(),
        property.FINAM_P_DAY: list(),
        property.FINAM_P_HOUR: list(),
    }
    incomes = {
        property.FINAM_P_MONTH: list(),
        property.FINAM_P_WEEK: list(),
        property.FINAM_P_DAY: list(),
        property.FINAM_P_HOUR: list(),
    }
    for company in companies:
        if count is None:
            count = company.month_history.__len__()
        line = [company.short_name, company.trade_code]
        for period in property.FINAM_PERIODS:
            risk_by_one = risk(count, history_by_period(period, company))
            income_by_one = income(count, history_by_period(period, company))
            risks[period].append(risk_by_one)
            incomes[period].append(income_by_one)
            if not re.compile(r'[0-9.-]').match(str(risk_by_one)) or \
                    not re.compile(r'[0-9.-]').match(str(income_by_one)):
                continue
            line.append(risk_by_one)
            line.append(income_by_one)
        if line.__len__() == 10:
            lines.append(line)

    lines.sort(key=lambda x: x[9])

    risk_periods = []
    incomes_periods = []
    try:
        for period in property.FINAM_PERIODS:
            covariance_m = covariance_matrix(companies, count, period)
            part, t_part = get_parts(companies)
            m_c_p = mmult(companies.__len__(), covariance_m, part)
            m_c_p_t = mmult(1, m_c_p, t_part)
            risk_periods.append(np.sqrt(m_c_p_t[0][0]))
            incomes_periods.append(get_all_incomes(incomes[period], part))
    except ValueError:
        LOG.warn('ValueError in covariance matrix')
        risk_periods = [0, 0, 0, 0]
        incomes_periods = [0, 0, 0, 0]
    for line in lines:
        lines_pattern.append(format(pattern % (line[0], line[1], line[2], line[3], line[4],
                                               line[5], line[6], line[7], line[8], line[9])))
    amount = '\nRisk_M: %.3f%% Income_M: %.3f%% ' \
             'Risk_W: %.3f%% Income_W: %.3f%% ' \
             'Risk_D: %.3f%% Income_D: %.3f%% ' \
             'Risk_H: %.3f%% Income_H: %.3f%% '
    return header + "\n".join(lines_pattern) + format(amount % (risk_periods[0], incomes_periods[0],
                                                                risk_periods[1], incomes_periods[1],
                                                                risk_periods[2], incomes_periods[2],
                                                                risk_periods[3], incomes_periods[3]
                                                                ))


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
    if period == property.FINAM_P_MONTH:
        return stock.month_history
    elif period == property.FINAM_P_WEEK:
        return stock.week_history
    elif period == property.FINAM_P_DAY:
        return stock.day_history
    elif period == property.FINAM_P_HOUR:
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
