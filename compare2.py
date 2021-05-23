#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""


import time

import matplotlib.pyplot as plt
import numpy as np

from bot.my_log import get_logger
from bot.analyse import solver, nsga as sm, nsga_platypus as nsagii
from bot.mongo import mongo as db

LOG = get_logger('compare-solver')

#iterations = [1000, 2000, 3000, 5000, 10000]#, 20000, 30000, 50000]
iterations = [2000]

# for ordered in db.get_portfolio_by_id('598dc26208ed83001321a939'):
for ordered in db.get_portfolio_by_id('60a1507fdb94780001237585'):
    sharpes_sm = list()
    sharpes_nsga = list()
    sharpes_nsgaiii = list()
    wgmean_sm = list()
    wgmean_nsga = list()
    wgmean_nsgaiii = list()
    time_sm = list()
    time_nsga = list()
    time_nsgaiii = list()
    trade_codes = list()
    for stock in ordered.max_item.stocks:
        trade_codes.append(stock.trade_code)

    stocks = list()
    for trade_code in trade_codes:
        stocks.append(db.stock_by_trade_code(trade_code))

    for num, iter in enumerate(iterations):
        fig = plt.figure('compare-' + str(iter))
        data = solver.get_stock_price(stocks)
        returns = data.pct_change()

        days = len(stocks[0].day_history)
        LOG.info('History length %d' % int(days))

        mean_daily_returns = returns.mean()
        cov_matrix = returns.cov()
        avr_gmean, gmeans = solver.average_gmean(returns)

        LOG.info('Geometric mean: %.8f, Daily meand: %.8f, Gmeans: %.8f' %
                 (avr_gmean, np.average(mean_daily_returns), gmeans))

        problemGenerator = nsagii.PortfolioGenerator(ordered)

        start = time.time()
        result_frame_sm = sm.solve(stocks, iter, mean_daily_returns, cov_matrix, days)
        time_sm_solve = time.time() - start
        time_sm.append(time_sm_solve)
        LOG.info('sm-%d - time: %s' % (iter, str(time_sm_solve)))

        ax = fig.add_subplot(1, 3, 1)
        id_max = result_frame_sm['sharpe'].idxmax()
        max_sharpe_port_sm = result_frame_sm.iloc[id_max]
        id_max_wgmean = result_frame_sm['wgmean'].idxmax()
        max_wgmean_port_sw = result_frame_sm.iloc[id_max_wgmean]
        sharpes_sm.append(max_sharpe_port_sm[2])
        wgmean_sm.append(max_wgmean_port_sw[1])

        ax.scatter(result_frame_sm.stdev, result_frame_sm.ret, c=result_frame_sm.sharpe, cmap='RdYlBu')
        ax.set_xlabel('stdev')
        ax.set_ylabel('ret')
        ax.scatter(max_sharpe_port_sm[2], max_sharpe_port_sm[0], marker=(3, 1, 0), color='r', s=300)
        ax.scatter(max_wgmean_port_sw[2], max_wgmean_port_sw[0], marker=(4, 2, 0), color='g', s=300)
        LOG.info('sm-%d: \nsharpe: \n %s \n wgmean \n %s ' % (iter, str(max_sharpe_port_sm), str(max_wgmean_port_sw)))
        plt.savefig("131.png")

