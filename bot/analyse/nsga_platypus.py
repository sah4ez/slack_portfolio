import platypus as pt
import numpy as np
import pandas as pd

import random

import my_log

LOG = my_log.get_logger('platypus')
from mongo.Stock import Stock
from mongo.Portfolio import Portfolio, Item, ItemPortfolio

all_stocks = list()
for s in Stock.objects():
    all_stocks.append(s)


class ProblemPortfolio(pt.Problem):
    def __init__(self, cov_matrix, mean_daily_returns, days):
        super(ProblemPortfolio, self).__init__(15, 2, nconstrs=1)

        self.cov_matrix = cov_matrix
        self.mean_daily_returns = mean_daily_returns
        self.days = days
        self.types[:] = pt.Real(0.0, 1.0)
        self.constraints[:] = "==1"

    def evaluate(self, solution):
        parts = np.array(solution.variables)
        solution.objectives[:] = [np.sum(self.mean_daily_returns * parts) * self.days,
                                  np.sqrt(np.dot(parts.T, np.dot(self.cov_matrix, parts))) * np.sqrt(self.days)]
        solution.constraints[:] = sum(parts)


def get_random_stocks(all_stocks):
    number = list()
    stocks = list()
    count = len(all_stocks)
    for position in range(15):
        pos = random.randint(0, count)
        while pos in number:
            pos = random.randint(0, count)
        stock = all_stocks[pos - 1]
        while len(stock.day_history) < 66:
            pos = random.randint(0, count)
            stock = all_stocks[pos - 1]
        stocks.append(stock)
    LOG.info('Found this stocks: %s ' % str(stocks))
    return stocks


def get_per_cent_by_item(stocks):
    data_list = list()
    for stock in stocks:
        price_stock = list()
        for price in stock.day_history:
            price_stock.append(price.value)
        data_list.append(price_stock)

    data = pd.DataFrame(data_list)
    return data.transpose().pct_change()


def solve(count):
    LOG.info('start NSGA with population count %d' % count)
    count_stocks = len(all_stocks)
    LOG.info('All stocks: %d' % count_stocks)
    result = list()
    for curr in range(count):
        random_stocks = get_random_stocks(all_stocks)
        days = len(all_stocks[0].day_history)
        returns = get_per_cent_by_item(random_stocks)
        mean_daily_returns = returns.mean()
        cov_matrix = returns.cov()
        LOG.info('Parameters: %s, %s, %s, %s' % (returns, mean_daily_returns, cov_matrix, days))
        problem = ProblemPortfolio(cov_matrix, mean_daily_returns, days)
        problem.directions[:] = [pt.Problem.MAXIMIZE, pt.Problem.MINIMIZE]
        algorithm = pt.NSGAII(problem)
        LOG.info('Start')
        algorithm.run(400000)
        LOG.info('End')
        result.append(algorithm.result)
        LOG.info('Solve: \n %s' % str(algorithm.result[0]))
    return str('OK')
