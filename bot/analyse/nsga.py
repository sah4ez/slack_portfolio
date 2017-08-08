import numpy as np
import pandas as pd
import my_log

LOG = my_log.get_logger('NSGA')


def solve(stocks, iterations, mean_daily_returns, cov_matrix, days):
    solver = SimpleSolver(stocks, mean_daily_returns, cov_matrix, days)
    results = solver.run(iterations)
    cols = ['ret', 'stdev', 'sharpe']
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
        results = np.zeros((4 + len(self.stocks) - 1, iterations))

        for i in range(iterations):
            weights = np.array(np.random.random(len(self.stocks)))
            weights /= np.sum(weights)

            portfolio_return = np.sum(self.mean_daily_returns * weights) * self.days
            portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights))) * np.sqrt(self.days)

            results[0, i] = portfolio_return
            results[1, i] = portfolio_std_dev
            results[2, i] = results[0, i] / results[1, i]
            for j in range(len(weights)):
                results[j + 3, i] = weights[j]

        return results
