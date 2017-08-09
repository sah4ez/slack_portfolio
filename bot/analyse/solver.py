import concurrent
import threading
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from mongo.Stock import Stock
from mongo.Portfolio import Portfolio, Item, ItemPortfolio
import random
import datetime
import my_log
import config
from analyse import nsga as simple, nsga_platypus as NSGAII
from concurrent.futures import ProcessPoolExecutor
import time
from mongo import mongo as db

LOG = my_log.get_logger('solver')


def get_stock_from_portfolio(portfolios):
    stocks = list()
    sharpes = list()
    for portfolio in portfolios:
        portfolio_stock = list()
        sharpes.append(portfolio.max_item.sharpe_ratio)
        for stock in portfolio.max_item.stocks:
            portfolio_stock.append(db.stock_by_trade_code(stock.trade_code))
        stocks.append(portfolio_stock)
    return stocks, sharpes


def parallel_solve(all_stocks, type_ga, curr, count):
    LOG.info('Start parallel solve in %s' % str(threading.get_ident()))
    range_stock = len(all_stocks)
    number = list()
    stocks = []

    for position in range(15):
        pos = random.randint(0, range_stock)
        while pos in number:
            pos = random.randint(0, range_stock)
        stock = all_stocks[pos - 1]
        while len(stock.day_history) < 66:
            pos = random.randint(0, range_stock)
            stock = all_stocks[pos - 1]
        stocks.append(stock)

    # download daily price data for each of the stocks in the portfolio
    data = get_stock_price(stocks)
    returns = data.pct_change()

    # calculate mean daily return and covariance of daily returns
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()
    days = len(stocks[0].day_history)
    iterations = 50000

    start = time.time()
    if type_ga == config.GA_SIMPLE:
        results_frame = simple.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    if type_ga == config.GA_NSGAII:
        results_frame = NSGAII.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    if type_ga == config.GA_NSGAIII:
        results_frame = NSGAII.solve_nsgaiii(stocks, iterations, mean_daily_returns, cov_matrix, days)
    duration = time.time() - start
    LOG.info('Duration solved: %s' % duration)

    max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
    min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

    LOG.info('Max Sharpe ratio: %s' % str(max_sharpe_port))
    LOG.info('Min standard deviation: %s' % str(min_vol_port))
    db.connect()
    solved = Portfolio()
    max_item = parse_solved_portfolio(max_sharpe_port, stocks)
    min_item = parse_solved_portfolio(min_vol_port, stocks)
    solved.max_item = max_item
    solved.min_item = min_item
    solved.date = datetime.datetime.today()
    solved.save()
    db.close()
    LOG.info('Save %d portfolio from %d in thread %s' % (curr, count, str(threading.get_ident())))
    return 'Duration %s' % str(duration)


def parse_solved_portfolio(array, stocks) -> ItemPortfolio:
    item_portfolio = ItemPortfolio()
    item_portfolio.returns = array[0]
    item_portfolio.standard_deviation = array[1]
    item_portfolio.sharpe_ratio = array[2]
    for num, stock_parts in enumerate(array[3:]):
        item = Item()
        item.value = stock_parts
        item.trade_code = stocks[num].trade_code
        item.exchange = 'ME'
        item_portfolio.stocks.append(item)
    return item_portfolio


def print_solve(results_frame, max_sharpe_port, min_vol_port):
    # create scatter plot coloured by Sharpe Ratio
    plt.scatter(results_frame.stdev, results_frame.ret, c=results_frame.sharpe, cmap='RdYlBu')
    plt.xlabel('Volatility')
    plt.ylabel('Returns')
    plt.colorbar()
    # plot red star to highlight position of portfolio with highest Sharpe Ratio
    plt.scatter(max_sharpe_port[1], max_sharpe_port[0], marker=(5, 1, 0), color='r', s=100)
    # plot green star to highlight position of minimum variance portfolio
    plt.scatter(min_vol_port[1], min_vol_port[0], marker=(5, 1, 0), color='g', s=100)
    plt.show()


def load_from_yahoo_finance(stocks):
    return web.DataReader(stocks, data_source='yahoo', start='01/01/2016')['Adj Close']


def get_stock_price(stocks):
    data_list = list()
    for stock in stocks:
        price_stock = list()
        for price in stock.day_history:
            price_stock.append(price.value)
        data_list.append(price_stock)
    data = pd.DataFrame(data_list)
    return data.transpose()


def cov_and_mean(stocks):
    # download daily price data for each of the stocks in the portfolio
    data = get_stock_price(stocks)
    returns = data.pct_change()

    # calculate mean daily return and covariance of daily returns
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()
    return cov_matrix, mean_daily_returns


def process_result_of_ga(results_frame, stocks):
    max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
    min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

    LOG.info('Max Sharpe ratio: \n%s' % str(max_sharpe_port))
    LOG.info('Min standard deviation: \n%s' % str(min_vol_port))
    db.connect()
    solved = Portfolio()
    max_item = parse_solved_portfolio(max_sharpe_port, stocks)
    min_item = parse_solved_portfolio(min_vol_port, stocks)
    solved.max_item = max_item
    solved.min_item = min_item
    solved.date = datetime.datetime.today()
    solved.save()
    db.close()
    return max_item.sharpe_ratio


def ga(words):
    if len(words) == 2:
        type_ga = words[0]
        count = int(words[1])
    else:
        return config.RSP_INVALID_PARAMETERS % str(words)

    LOG.info('start NSGA with population count %d' % count)
    all_stocks = list()
    db.connect()
    for s in Stock.objects():
        all_stocks.append(s)
    db.close()
    print(len(all_stocks))
    with ProcessPoolExecutor(max_workers=2) as executor:
        features = {executor.submit(parallel_solve, all_stocks, type_ga, curr, count): curr for curr in range(count)}
        for feature in concurrent.futures.as_completed(features):
            LOG.info('Complete %s ' % feature.result())
    return config.RSP_GA


def optimize(words):
    repeats = 1
    if len(words) == 4:
        type_ga = words[1]
        iterations = int(words[2])
        count = int(words[3])
    if len(words) == 5:
        type_ga = words[1]
        iterations = int(words[2])
        count = int(words[3])
        repeats = int(words[4])
    else:
        return config.RSP_INVALID_PARAMETERS % str(words)

    result = list()
    LOG.info('Start optimization with %s [%d] for %d' % (type_ga, iterations, count))
    for repeat in range(repeats):
        LOG.info('Repeat %d / %d' % (repeat, repeats))

        portfolios = db.get_n_first_portfolios(count)

        all_stocks, sharpes = get_stock_from_portfolio(portfolios)
        optimize_sharpes = list()
        with ProcessPoolExecutor() as executor:
            features = {
                executor.submit(parallel_optimization, portfolios.index(portfolio), portfolios, portfolio, all_stocks,
                                iterations, type_ga): portfolio for portfolio in portfolios}
            for feature in concurrent.futures.as_completed(features):
                optimize_sharpes.append(feature.result())
        for num, x in enumerate(sharpes):
            y = optimize_sharpes[num]
        result.append(format('%s | %.4f -> %.4f ==> %.4f%%' % (str(portfolios[num]._id), x, y, y / x * 100)))
    return "Result: \n" + "\n".join(result)


def parallel_optimization(num, portfolios, portfolio, all_stocks, iterations, type_ga):
    stocks = all_stocks[num]
    days = len(stocks[0].day_history)
    cov_matrix, mean_daily_returns = cov_and_mean(stocks)
    problemGenerator = NSGAII.PortfolioGenerator(portfolio)

    start = time.time()
    if type_ga == config.GA_SIMPLE:
        results_frame = simple.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    if type_ga == config.GA_NSGAII:
        results_frame = NSGAII.solve(stocks, iterations, mean_daily_returns, cov_matrix, days, problemGenerator)
    if type_ga == config.GA_NSGAIII:
        results_frame = NSGAII.solve_nsgaiii(stocks, iterations, mean_daily_returns, cov_matrix, days,
                                             problemGenerator)
    duration = time.time() - start
    LOG.info('Duration solved: %s' % duration)
    new_sharpe = process_result_of_ga(results_frame, stocks)
    LOG.info('Solve %d of %d' % (num + 1, len(portfolios)))
    return new_sharpe


def parallel_solve(all_stocks, type_ga, curr, count):
    LOG.info('Start parallel solve in %s' % str(threading.get_ident()))
    range_stock = len(all_stocks)
    number = list()
    stocks = []

    for position in range(15):
        pos = random.randint(0, range_stock)
        while pos in number:
            pos = random.randint(0, range_stock)
        stock = all_stocks[pos - 1]
        while len(stock.day_history) < 66:
            pos = random.randint(0, range_stock)
            stock = all_stocks[pos - 1]
        stocks.append(stock)

    cov_matrix, mean_daily_returns = cov_and_mean(stocks)
    days = len(stocks[0].day_history)
    iterations = 50000

    start = time.time()
    if type_ga == config.GA_SIMPLE:
        results_frame = simple.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    if type_ga == config.GA_NSGAII:
        results_frame = NSGAII.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    if type_ga == config.GA_NSGAIII:
        results_frame = NSGAII.solve_nsgaiii(stocks, iterations, mean_daily_returns, cov_matrix, days)
    duration = time.time() - start
    LOG.info('Duration solved: %s' % duration)
    process_result_of_ga(results_frame, stocks)
    LOG.info('Save %d portfolio from %d in thread %s' % (curr, count, str(threading.get_ident())))
    return 'Duration %s' % str(duration)
