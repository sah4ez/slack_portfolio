import concurrent
import datetime
import random
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from os import environ as env

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader.data as web
from scipy.stats import mstats as ms

from bot.config import GA_NSGAII, RSP_INVALID_PARAMETERS, GA_SIMPLE, GA_NSGAIII
from bot.my_log import get_logger
from bot.analyse import nsga as simple, nsga_platypus as NSGAII
from bot.mongo import mongo as db
from bot.mongo.Portfolio import Portfolio, Item, ItemPortfolio
from bot.mongo.Stock import Stock
from bot.property import *

LOG = get_logger('solver')


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
    if type_ga == GA_SIMPLE:
        results_frame = simple.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    if type_ga == GA_NSGAII:
        results_frame = NSGAII.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    if type_ga == GA_NSGAIII:
        results_frame = NSGAII.solve_nsgaiii(stocks, iterations, mean_daily_returns, cov_matrix, days)
    duration = time.time() - start
    LOG.info('Duration solved: %s' % duration)

    sharpe_id_min = results_frame['sharpe'].idxmin()
    max_sharpe_port = results_frame.iloc[sharpe_id_min]
    stdev_id_min = results_frame['stdev'].idxmax()
    min_vol_port = results_frame.iloc[stdev_id_min]

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
    LOG.info('Save %d portfolio from %d in thread %s' % (curr+1, count, str(threading.get_ident())))
    return 'Duration %s' % str(duration)


def parse_solved_portfolio(array, stocks) -> ItemPortfolio:
    item_portfolio = ItemPortfolio()
    item_portfolio.returns = array[0]
    item_portfolio.wgmean = array[1]
    item_portfolio.standard_deviation = array[2]
    item_portfolio.sharpe_ratio = array[3]
    for num, stock_parts in enumerate(array[4:]):
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
    avr_gmean, gmeans = average_gmean(returns)

    # calculate mean daily return and covariance of daily returns
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()
    return cov_matrix, mean_daily_returns, avr_gmean, gmeans


def average_gmean(returns):
    full_returns = np.array(returns[1:len(returns) - 1])
    full_returns += 1
    avr = 0
    count = 0
    gmeans = list()
    for ret in full_returns[1:].T:
        avr += ms.gmean(ret)
        gmeans.append(ms.gmean(ret))
        count += 1
    return avr / count, ms.gmean(gmeans)


def weigth_geom_mean(means, parts):
    return np.exp(sum([parts[num] * np.log(mean) for num, mean in enumerate(means)]) / np.sum(parts))


def process_result_of_ga(results_frame, stocks, gmean):
    try:
        id_sharpe = results_frame['sharpe'].idxmax()
    except TypeError as exc:
        id_sharpe = maxId(results_frame, 'sharpe')

    try:
        max_sharpe_port = results_frame.iloc[id_sharpe]
    except TypeError as exc:
        id_sharpe = maxId(results_frame, 'sharpe')
        max_sharpe_port = results_frame.iloc[id_sharpe]

    try:
        id_stdev = results_frame['stdev'].idxmin()
    except TypeError as exc:
        id_stdev = minId(results_frame, 'stdev')

    if id_stdev == np.NaN:
        id_stdev = minId(results_frame, 'stdev')

    try:
        min_vol_port = results_frame.iloc[id_stdev]
    except TypeError as exc:
        id_stdev = minId(results_frame, 'stdev')
        min_vol_port = results_frame.iloc[id_stdev]

    LOG.info('Max Sharpe ratio: \n%s' % str(max_sharpe_port))
    LOG.info('Min standard deviation: \n%s' % str(min_vol_port))
    db.connect()
    solved = Portfolio()
    max_item = parse_solved_portfolio(max_sharpe_port, stocks)
    min_item = parse_solved_portfolio(min_vol_port, stocks)
    solved.max_item = max_item
    solved.min_item = min_item
    solved.date = datetime.datetime.today()
    solved.total_sum = 0
    for stock in max_item.stocks:
        solved.total_sum += stock.value
    if gmean is None:
        solved.gmean = 0.0
    else:
        solved.gmean = gmean
    solved.save()
    db.close()
    return max_item.sharpe_ratio, solved._id


def maxId(results_frame, key):
    LOG.info("frame %s" % results_frame[key])
    sharpe = 0
    id_item = 0
    for num, x in enumerate(results_frame[key]):
        if sharpe < x:
            sharpe = x
            id_item = num
    return id_item


def minId(results_frame, key):
    LOG.info("frame %s" % results_frame[key])
    sharpe = 0
    id_item = 0
    for num, x in enumerate(results_frame[key]):
        if sharpe > x:
            sharpe = x
            id_item = num
    return id_item


def optimize(words):
    repeats = 1
    if 'repeat' in words:
        position = list(words).index('repeat')
        words.pop(position)
        repeats = int(words.pop(position))

    if len(words) == 3:
        type_ga = words[1]
        iterations = int(words[2])
        count = 0
    elif len(words) == 4:
        type_ga = words[1]
        iterations = int(words[2])
        count = int(words[3])
    elif len(words) == 5:
        type_ga = words[1]
        iterations = int(words[2])
        count = int(words[3])
        repeats = int(words[4])
    else:
        LOG.error(RSP_INVALID_PARAMETERS % str(words))
        return RSP_INVALID_PARAMETERS % str(words)

    result = list()
    LOG.info('Start optimization with %s [%d] for %d' % (type_ga, iterations, count))
    for repeat in range(repeats):
        LOG.info('Repeat %d / %d' % (repeat, repeats))

        if count == 0:
            portfolios = db.get_n_random_portfolios()
        else:
            portfolios = db.get_n_first_portfolios(count)

        all_stocks, sharpes = get_stock_from_portfolio(portfolios)
        optimize_sharpes = list()
        ids = list()
        if PARALLEL:
            workers = env.get(THREAD)
            if workers is None:
                workers = 1
            with ProcessPoolExecutor(max_workers=int(workers)) as executor:
                features = {
                    executor.submit(parallel_optimization, num, portfolios, portfolio, all_stocks, iterations, type_ga):
                        [num, portfolio] for num, portfolio in enumerate(portfolios)}
                for feature in concurrent.futures.as_completed(features):
                    shapre, id = feature.result()
                    optimize_sharpes.append(shapre)
                    ids.append(id)
        else:
            for num, portfolio in enumerate(portfolios):
                shapre, id = parallel_optimization(num, portfolios, portfolio, all_stocks, iterations, type_ga)
                optimize_sharpes.append(shapre)
                ids.append(id)
        for num, x in enumerate(sharpes):
            y = optimize_sharpes[num]
            result.append(format('%s | %.4f -> %.4f ==> %.4f%%' % (str(ids[num]), x, y, y / x * 100)))
    return "Result: \n" + "\n".join(result)


def parallel_optimization(num, portfolios, portfolio, all_stocks, iterations, type_ga):
    stocks = all_stocks[num]
    days = len(stocks[0].day_history)
    cov_matrix, mean_daily_returns, avr_gmean, gmeans = cov_and_mean(stocks)
    problemGenerator = NSGAII.PortfolioGenerator(portfolio)

    start = time.time()
    if type_ga == GA_SIMPLE:
        results_frame = simple.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    elif type_ga == GA_NSGAII:
        results_frame = NSGAII.solve(stocks, iterations, mean_daily_returns, cov_matrix, days,
                                     generator=problemGenerator)
    else:
        results_frame = NSGAII.solve_nsgaiii(stocks, iterations, mean_daily_returns, cov_matrix, days,
                                             generator=problemGenerator)
    duration = time.time() - start
    LOG.info('Duration solved: %s' % duration)
    new_sharpe, new_id = process_result_of_ga(results_frame, stocks, avr_gmean)
    LOG.info('Solve %d of %d' % (num + 1, len(portfolios)))
    return new_sharpe, new_id


def parallel_solve_WTF_im_very_sad(all_stocks, type_ga, curr, count):
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
        number.append(pos)
        stocks.append(stock)

    cov_matrix, mean_daily_returns, arg_gmean, gmeans = cov_and_mean(stocks)
    days = len(stocks[0].day_history)
    iterations = 50000

    start = time.time()
    if type_ga == GA_SIMPLE:
        results_frame = simple.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    elif type_ga == GA_NSGAII:
        results_frame = NSGAII.solve(stocks, iterations, mean_daily_returns, cov_matrix, days)
    else:
        results_frame = NSGAII.solve_nsgaiii(stocks, iterations, mean_daily_returns, cov_matrix, days)
    duration = time.time() - start
    LOG.info('Duration solved: %s' % duration)
    process_result_of_ga(results_frame, stocks, arg_gmean)
    LOG.info('Save %d portfolio from %d in thread %s' % (curr, count, str(threading.get_ident())))
    return 'Duration %s' % str(duration)


def ga(words):
    if len(words) == 2:
        type_ga = words[0]
        count = int(words[1])
    else:
        return RSP_INVALID_PARAMETERS % str(words)

    LOG.info('start NSGA with population count %d' % count)
    all_stocks = list()
    db.connect()
    for s in Stock.objects():
        all_stocks.append(s)
    db.close()
    print(len(all_stocks))
    if PARALLEL:
        workers = env.get(THREAD)
        if workers is None:
            workers = 1
        with ProcessPoolExecutor(max_workers=int(workers)) as executor:
            features = {executor.submit(parallel_solve, all_stocks, type_ga, curr, count): curr for curr in range(count)}
            for feature in concurrent.futures.as_completed(features):
                LOG.info('Complete %s ' % feature.result())
    else:
        for curr in range(count):
            parallel_solve(all_stocks, type_ga, curr, count)
    return 'Finish GA!'
