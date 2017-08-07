import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from pandas_datareader._utils import RemoteDataError
from mongo.Stock import Stock
from mongo import mongo as db
import random
import datetime
from slackclient import SlackClient
import bot
import shutil

# list of stocks in portfolio
def ga(slack_client: SlackClient, channel, count=150):
    all_stocks = []
    for s in Stock.objects():
        all_stocks.append(s)
    print(len(all_stocks))
    portfolios = count
    for portfolio in range(portfolios):
        range_stock = len(all_stocks)
        number = list()
        stocks = []

        # for position in range(15):
        #     pos = random.randint(0, range_stock)
        #     while pos in number:
        #         pos = random.randint(0, range_stock)
        #     stock = all_stocks[pos - 1]
        #     while len(stock.day_history) < 44:
        #         pos = random.randint(0, range_stock)
        #         stock = all_stocks[pos - 1]
        #     stocks.append(stock)

        trade_codes = ['FESH', 'RTKMP', 'GMKN', 'OPIN', 'RUGR', 'VSMO', 'NMTP', 'MGNT', 'LNZLP', 'TUCH', 'IRKT',
                       'PRTK', 'TGKB', 'BANEP', 'ROSN']

        for code in trade_codes:
            stocks.append(db.stock_by_trade_code(code))
        # stocks = ['LKOH.ME', 'SBER.ME', 'HYDR.ME', 'ALRS.ME', 'TATNP.ME', 'IRAO.ME']
        # stocks = ['AAPL', 'MSFT', 'AMZN']
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

        #slack_client.api_call("chat.postMessage", channel=channel,
        #                      text=", ".join(resp), as_user=True)

        # i = 0
        # ex = True
        # while i < 10 and ex:
        #     try:
        #         ex = False
        #         data = web.DataReader(stocks, data_source='yahoo', start='01/01/2016')['Adj Close']
        #     except RemoteDataError:
        #         i += 1
        #         ex = True
        #
        # print('Loaded')

        # convert daily stock prices into daily returns
        # returns = data.pct_change()

        # calculate mean daily return and covariance of daily returns
        mean_daily_returns = returns.mean()
        cov_matrix = returns.cov()

        # set number of runs of random portfolio weights
        num_portfolios = 400_000

        # set up array to hold results
        # We have increased the size of the array to hold the weight values for each stock
        results = np.zeros((4 + len(stocks) - 1, num_portfolios))

        for i in range(num_portfolios):
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
            #if i in [100_000 - 1, 200_000 - 1, 300_000 - 1]:
            #    slack_client.api_call("chat.postMessage", channel=channel,
            #                          text='i: ' + str(i) + 'portfolio' + str(portfolio), as_user=True)

        # convert results array to Pandas DataFrame
        cols = ['ret', 'stdev', 'sharpe']
        for s in stocks:
            cols.append(s.shape())
        results_frame = pd.DataFrame(results.T, columns=cols)

        # locate position of portfolio with highest Sharpe Ratio
        max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
        # locate positon of portfolio with minimum standard deviation
        min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

        # create scatter plot coloured by Sharpe Ratio
        # plt.scatter(results_frame.stdev, results_frame.ret, c=results_frame.sharpe, cmap='RdYlBu')
        # plt.xlabel('Volatility')
        # plt.ylabel('Returns')
        # plt.colorbar()
        # plot red star to highlight position of portfolio with highest Sharpe Ratio
        # plt.scatter(max_sharpe_port[1], max_sharpe_port[0], marker=(5, 1, 0), color='r', s=100)
        # plot green star to highlight position of minimum variance portfolio
        # plt.scatter(min_vol_port[1], min_vol_port[0], marker=(5, 1, 0), color='g', s=100)
        print(datetime.datetime.now())
        print(max_sharpe_port, '\n')
        print(min_vol_port)
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=str(max_sharpe_port) + '\n' + str(min_vol_port), as_user=True)
        with open('res/output.txt', 'a') as file:
            file.write(str(max_sharpe_port))
            file.write('----------')
            file.write(str(min_vol_port))
            file.write('==========')
            file.flush()
            file.close()
        # with open('res/max_output_table.txt', 'w+') as file:
        #     file.write(max_sharpe_port[0] + ';' + max_sharpe_port[1])
        #     file.flush()
        #     file.close()
        # with open('res/min_output_table.txt', 'w+') as file:
        #     file.write(min_vol_port[0] + ';' + min_vol_port[1])
        #     file.flush()
        #     file.close()
        print('')
    shutil.copyfile('res/output.txt','res/output_back.txt')
    bot.post_file(channel, 'res/output_back.txt')
