import random

import numpy as np
import pandas as pd
import platypus as pt

from bot.my_log import get_logger
from bot.mongo import mongo as db
from bot.mongo.Stock import Stock

LOG = get_logger('platypus')
db.connect()
all_stocks = list()
for s in Stock.objects():
    all_stocks.append(s)
db.close()


class ProblemPortfolio(pt.Problem):
    def __init__(self, cov_matrix, mean_daily_returns, days):
        super(ProblemPortfolio, self).__init__(nvars=15, nobjs=2, nconstrs=4)

        self.cov_matrix = cov_matrix
        self.mean_daily_returns = mean_daily_returns
        self.days = days
        self.types[:] = pt.Real(0.0, 1.0)
        self.constraints.__setitem__(0, "==1")
        self.constraints.__setitem__(1, "<=0.06")
        self.constraints.__setitem__(2, ">=0.02")
        self.constraints.__setitem__(3, "<=0.18")

    def evaluate(self, solution):
        parts = np.array(solution.variables)
        parts /= np.sum(parts)
        solution.variables = parts

        solution.objectives[:] = [np.sum(-1*self.mean_daily_returns * solution.variables) * self.days,
                                  np.exp(sum([solution.variables[num] * -1 * np.log(1 + mean) for num, mean in
                                              enumerate(self.mean_daily_returns)]) / np.sum(solution.variables))]

        solution.stdev = np.sqrt(np.dot(solution.variables.T,
                                        np.dot(self.cov_matrix, solution.variables))) * np.sqrt(self.days)

        solution.constraints[:] = [np.sum(solution.variables),
                                   np.sqrt(np.dot(solution.variables.T,
                                                  np.dot(self.cov_matrix, solution.variables))) * np.sqrt(self.days),
                                   min(solution.variables),
                                   max(solution.variables)]


class PortfolioSolution(pt.Solution):
    def __init__(self, problem):
        super().__init__(problem)
        self.stdev = 0.0


class PortfolioGenerator(pt.Generator):
    def __init__(self, portfolio):
        super(PortfolioGenerator, self).__init__()
        self.portfolio = portfolio
        self.step = 0.005

    def generate(self, problem):
        solution = PortfolioSolution(problem)
        solution.variables = [self.shift(x.value) for x in self.portfolio.max_item.stocks]
        solution.variables /= np.sum(solution.variables)
        return solution

    def shift(self, x):
        values = pt.Real(-1, 1)
        sign = values.rand()
        x += sign
        if x > 1:
            x -= 1
        elif x < 0:
            x *= -1
        return x


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


def algorithm(stocks, iterations, NSGA, population=100):
    NSGA.population_size = population
    NSGA.run(iterations)
    cols = ['ret', 'wgmean', 'stdev', 'sharpe']
    results = np.zeros((NSGA.population_size, len(cols) + len(stocks)))
    for num, solution in enumerate(NSGA.result):
        results[num][0] = -1*solution.objectives[0]
        results[num][1] = -1*solution.objectives[1]
        results[num][2] = -1*solution.stdev
        results[num][3] = -1*results[num][0] / -1*results[num][2]
        results[num][4:] = np.array(solution.variables)
    for stock in stocks:
        cols.append(stock.shape())
    results_frame = pd.DataFrame(results, columns=cols)
    return results_frame


def solve(stocks, iterations, mean_daily_returns, cov_matrix, days, population=100, generator: pt.Generator = None):
    LOG.info('Start nsgaII for %d . Generator is default %s' % (iterations, generator is None))

    problem = ProblemPortfolio(cov_matrix, mean_daily_returns, days)
    #  problem.directions[:] = [pt.Problem.MAXIMIZE, pt.Problem.MAXIMIZE]
    problem.directions[:] = [pt.Problem.MINIMIZE, pt.Problem.MINIMIZE]
    if generator is None:
        nsga = pt.NSGAII(problem)
    else:
        nsga = pt.NSGAII(problem, generator=generator)
    return algorithm(stocks, iterations, nsga, population)


def solve_nsgaiii(stocks, iterations, mean_daily_returns, cov_matrix, days, population=100,
                  generator: pt.Generator = None):
    LOG.info('Start nsgaIII for %d . Generator is default %s' % (iterations, generator is None))
    problem = ProblemPortfolio(cov_matrix, mean_daily_returns, days)
    #  problem.directions[:] = [pt.Problem.MAXIMIZE, pt.Problem.MAXIMIZE]
    problem.directions[:] = [pt.Problem.MINIMIZE, pt.Problem.MINIMIZE]
    if generator is None:
        nsgaiii = pt.NSGAIII(problem, divisions_outer=1, divisions_inner=1)
    else:
        nsgaiii = pt.NSGAIII(problem, divisions_outer=1, divisions_inner=1, generator=generator)
    return algorithm(stocks, iterations, nsgaiii, population)
