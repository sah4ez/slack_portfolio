import time

import matplotlib.pyplot as plt
import numpy as np

from bot.my_log import get_logger
from bot.analyse import solver, nsga as sm, nsga_platypus as nsagii
from bot.mongo import mongo as db

LOG = get_logger('compare-solver')

#iterations = [1000, 2000, 3000, 5000, 10000]#, 20000, 30000, 50000]
iterations = [50000]

# for ordered in db.get_portfolio_by_id('598dc26208ed83001321a939'):
for ordered in db.get_portfolio_by_id('59dfa8d956840e758733884e'):
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
        plt.figure('compare-' + str(iter))
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

        start = time.time()
        result_frame_nsgaii = nsagii.solve(stocks, iter, mean_daily_returns, cov_matrix, days,
                                           generator=problemGenerator, population=1000)
        time_nsga_solve = time.time() - start
        time_nsga.append(time_nsga_solve)
        LOG.info('nsgaii-%d - time: %s' % (iter, str(time_nsga_solve)))

        start = time.time()
        result_frame_nsgaiii = nsagii.solve_nsgaiii(stocks, iter, mean_daily_returns, cov_matrix, days,
                                                    generator=problemGenerator, population=1000)
        time_nsga_solve = time.time() - start
        time_nsgaiii.append(time_nsga_solve)
        LOG.info('nsagiii-%d - time: %s' % (iter, str(time_nsga_solve)))

        plt.subplot(131)
        id_max = result_frame_sm['sharpe'].idxmax()
        max_sharpe_port_sm = result_frame_sm.iloc[id_max]
        id_max_wgmean = result_frame_sm['wgmean'].idxmax()
        max_wgmean_port_sw = result_frame_sm.iloc[id_max_wgmean]
        sharpes_sm.append(max_sharpe_port_sm[2])
        wgmean_sm.append(max_wgmean_port_sw[1])
        plt.scatter(result_frame_sm.stdev, result_frame_sm.ret, c=result_frame_sm.sharpe, cmap='RdYlBu')
        plt.xlabel('stdev')
        plt.ylabel('ret')
        plt.scatter(max_sharpe_port_sm[2], max_sharpe_port_sm[0], marker=(3, 1, 0), color='r', s=300)
        plt.scatter(max_wgmean_port_sw[2], max_wgmean_port_sw[0], marker=(4, 2, 0), color='g', s=300)
        LOG.info('sm-%d: \nsharpe: \n %s \n wgmean \n %s ' % (iter, str(max_sharpe_port_sm), str(max_wgmean_port_sw)))

        plt.subplot(132)
        id_max = result_frame_nsgaii['sharpe'].idxmax()
        max_sharpe_port_nsgaii = result_frame_nsgaii.iloc[id_max]
        id_max_wgmean = result_frame_nsgaii['wgmean'].idxmax()
        max_wgmean_port_nsgaii = result_frame_nsgaii.iloc[id_max_wgmean]
        sharpes_nsga.append(max_sharpe_port_nsgaii[2])
        wgmean_nsga.append(max_wgmean_port_nsgaii[1])
        plt.scatter(result_frame_nsgaii.stdev, result_frame_nsgaii.ret, c=result_frame_nsgaii.sharpe, cmap='RdYlBu')
        plt.xlabel('stdev')
        plt.ylabel('ret')
        plt.scatter(max_sharpe_port_nsgaii[2], max_sharpe_port_nsgaii[0], marker=(5, 1, 0), color='r', s=300)
        plt.scatter(max_wgmean_port_nsgaii[2], max_wgmean_port_nsgaii[0], marker=(6, 2, 0), color='g', s=300)
        LOG.info(
            'nsgaii-%d: sharpe\n %s \n wgmean \n %s' % (iter, str(max_sharpe_port_nsgaii), str(max_wgmean_port_nsgaii)))

        plt.subplot(133)
        id_max = result_frame_nsgaiii['sharpe'].idxmax()
        max_sharpe_port_nsgaiii = result_frame_nsgaiii.iloc[id_max]
        id_max_wgmean = result_frame_nsgaiii['sharpe'].idxmax()
        max_wgmean_port_nsgaiii = result_frame_nsgaiii.iloc[id_max_wgmean]
        sharpes_nsgaiii.append(max_sharpe_port_nsgaiii[2])
        wgmean_nsgaiii.append(max_wgmean_port_nsgaiii[1])
        plt.scatter(result_frame_nsgaiii.stdev, result_frame_nsgaiii.ret, c=result_frame_nsgaiii.sharpe, cmap='RdYlBu')
        plt.xlabel('stdev')
        plt.ylabel('ret')
        plt.scatter(max_sharpe_port_nsgaiii[2], max_sharpe_port_nsgaiii[0], marker=(6, 2, 0), color='r', s=300)
        plt.scatter(max_wgmean_port_nsgaiii[2], max_wgmean_port_nsgaiii[0], marker=(7, 2, 0), color='g', s=300)
        LOG.info('nsgaiii-%d: \n sharpe \n %s \n wgmean \n %s' % (
            iter, str(max_sharpe_port_nsgaiii), str(max_wgmean_port_nsgaiii)))

        LOG.info('%d / %d' % (num + 1, len(iterations)))

    plt.figure('trend')
    plt.plot(iterations, sharpes_sm, label='sm')
    plt.plot(iterations, sharpes_nsga, label='nsgaii')
    plt.plot(iterations, sharpes_nsgaiii, label='nsgaiii')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    plt.figure('trend_wgmean')
    plt.plot(iterations, wgmean_sm, label='sm')
    plt.plot(iterations, wgmean_nsga, label='nsgaii')
    plt.plot(iterations, wgmean_nsgaiii, label='nsgaiii')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    plt.figure('time')
    plt.plot(iterations, time_sm, label='sm')
    plt.plot(iterations, time_nsga, label='nsgaii')
    plt.plot(iterations, time_nsgaiii, label='nsgaiii')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.show()
