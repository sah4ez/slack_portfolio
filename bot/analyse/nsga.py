import concurrent

import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from pandas_datareader._utils import RemoteDataError
from mongo.Stock import Stock
from mongo.Portfolio import Portfolio, Item, ItemPortfolio
from mongo import mongo as db
import random
import datetime
from slackclient import SlackClient
import shutil
import my_log
import re
from concurrent.futures import ThreadPoolExecutor

LOG = my_log.get_logger('NSGA')


# list of stocks in portfolio
def ga(slack_client: SlackClient, channel, count=150):
    LOG.info('start NSGA with population count %d' % count)
    all_stocks = list()
    for s in Stock.objects():
        all_stocks.append(s)
    print(len(all_stocks))
    for curr in range(count):
        solve(all_stocks, slack_client, channel, curr, count)
    # with ThreadPoolExecutor() as executor:
    #     all_feature = {executor.submit(solve, all_stocks, slack_client, channel, curr, count): curr for curr in
    #                range(count)}
    #     for future in concurrent.futures.as_completed(all_feature):
    #         solve_fetaure = all_feature[future]
    #         try:
    #             data = future.result()
    #         except Exception as exc:
    #             LOG.error('%r generated an exception: %s' % (solve_fetaure, exc))
    #         else:
    #             LOG.info('Successful!')

    shutil.copyfile('res/output.txt', 'res/output_back.txt')


def solve(all_stocks, slack_client, channel, curr, all_items):
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
    data_list = list()
    for stock in stocks:
        price_stock = list()
        for price in stock.day_history:
            price_stock.append(price.value)
        data_list.append(price_stock)

    data = pd.DataFrame(data_list)
    returns = data.transpose().pct_change()
    resp = list()
    for stock in stocks:
        resp.append(stock.shape())

    # convert daily stock prices into daily returns
    # returns = data.pct_change()

    # calculate mean daily return and covariance of daily returns
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()

    # set number of runs of random portfolio weights
    iterations = 400_000

    # set up array to hold results
    # We have increased the size of the array to hold the weight values for each stock
    results = np.zeros((4 + len(stocks) - 1, iterations))
    LOG.info('Start optimization with %d iteration' % iterations)
    for i in range(iterations):
        # select random weights for portfolio holdings
        weights = np.array(np.random.random(len(stocks)))
        # rebalance weights to sum to 1
        weights /= np.sum(weights)

        # calculate portfolio return and volatility
        portfolio_return = np.sum(mean_daily_returns * weights) * 252
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)

        # store results in results array
        results[0, i] = portfolio_return
        results[1, i] = portfolio_std_dev
        # store Sharpe Ratio (return / volatility) - risk free rate element excluded for simplicity
        results[2, i] = results[0, i] / results[1, i]
        # iterate through the weight vector and add data to results array
        for j in range(len(weights)):
            results[j + 3, i] = weights[j]
        if re.compile('[0-9]00000').match(str(i)):
            LOG.info('Solved %d iteration' % i)

    # convert results array to Pandas DataFrame
    cols = ['ret', 'stdev', 'sharpe']
    for s in stocks:
        cols.append(s.shape())
    results_frame = pd.DataFrame(results.T, columns=cols)

    # locate position of portfolio with highest Sharpe Ratio
    max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
    # locate positon of portfolio with minimum standard deviation
    min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

    LOG.info('Max Sharpe ratio: %s' % str(max_sharpe_port))
    LOG.info('Min standard deviation: %s' % str(min_vol_port))
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=str(max_sharpe_port) + '\n' + str(min_vol_port), as_user=True)
    solved = Portfolio()
    max_item = parse_solved_portfolio(max_sharpe_port, stocks)
    min_item = parse_solved_portfolio(min_vol_port, stocks)
    solved.max_item = max_item
    solved.min_item = min_item
    solved.date = datetime.datetime.today()
    solved.save()
    LOG.info('Save %d portfolio from %d' % (curr, all_items))
    with open('res/output.txt', 'a') as file:
        file.write(str(max_sharpe_port))
        file.write('----------')
        file.write(str(min_vol_port))
        file.write('==========')
        file.flush()
        file.close()
    return 0


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
