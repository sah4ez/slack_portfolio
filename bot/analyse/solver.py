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
import config
from analyse import nsga as simple, nsga_platypus as NSGAII

LOG = my_log.get_logger('solver')


def ga(slack_client: SlackClient, channel, count=150, type=config.GA_SIMPLE):
    LOG.info('start NSGA with population count %d' % count)
    all_stocks = list()
    for s in Stock.objects():
        all_stocks.append(s)
    print(len(all_stocks))
    for curr in range(count):
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
        if type == config.GA_SIMPLE:
            results_frame = simple.solve(all_stocks, 400000, mean_daily_returns, cov_matrix, days)
        if type == config.GA_NSGAII:
            results_frame = NSGAII.solve(all_stocks, 400000, mean_daily_returns, cov_matrix, days)

        max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
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
        LOG.info('Save %d portfolio from %d' % (curr, count))
        with open('res/output.txt', 'a') as file:
            file.write(str(max_sharpe_port))
            file.write('----------')
            file.write(str(min_vol_port))
            file.write('==========')
            file.flush()
            file.close()

    shutil.copyfile('res/output.txt', 'res/output_back.txt')


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
