import numpy as np
import pandas as pd

from bot.my_log import get_logger

LOG = get_logger('NSGA')


def solve(stocks, iterations, mean_daily_returns, cov_matrix, days):
    LOG.info('Start simple GA for %d' % iterations)
    solver = SimpleSolver(stocks, mean_daily_returns, cov_matrix, days)
    results = solver.run(iterations)
    cols = ['ret', 'wgmean', 'stdev', 'sharpe']
    for stock in stocks:
        cols.append(stock.shape())
    results_frame = pd.DataFrame(results.T, columns=cols)
    return results_frame


class SimpleSolver:
    def __init__(self, stocks, mean_daily_returns, cov_matrix, days) -> None:
        self.stocks = stocks
        self.mean_daily_returns = mean_daily_returns
        self.cov_matrix = cov_matrix
        self.days = days

    def run(self, iterations):
        cols = 4
        results = np.zeros((cols + len(self.stocks), iterations))

        for i in range(iterations):
            weights = np.array(np.random.random(len(self.stocks)))
            weights /= np.sum(weights)

            portfolio_return = np.sum(self.mean_daily_returns * weights) * self.days
            portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights))) * np.sqrt(self.days)
            portfolio_weigth_geom_mean = \
                np.exp(
                    sum([weights[num] * np.log(1 + mean) for num, mean in enumerate(self.mean_daily_returns)])
                    / np.sum(weights))

            results[0, i] = portfolio_return
            results[1, i] = portfolio_weigth_geom_mean
            results[2, i] = portfolio_std_dev
            results[3, i] = results[0, i] / results[2, i]
            for j in range(len(weights)):
                results[j + cols, i] = weights[j]

        return results
