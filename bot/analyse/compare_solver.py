import matplotlib.pyplot as plt
import my_log
from mongo import mongo as db
from analyse import solver, nsga as sm, nsga_platypus as nsagii
import time

LOG = my_log.get_logger('compare-solver')


iterations = [150000, 200000, 250000]
# iterations = [300000]

for ordered in db.get_n_first_portfolios(1):
    sharpes_sm = list()
    sharpes_nsga = list()
    sharpes_nsgaiii = list()
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
        mean_daily_returns = returns.mean()
        cov_matrix = returns.cov()

        start = time.time()
        result_frame_sm = sm.solve(stocks, iter, mean_daily_returns, cov_matrix, days)
        time_sm_solve = time.time() - start
        time_sm.append(time_sm_solve)
        LOG.info('sm-%d - time: %s' % (iter, str(time_sm_solve)))

        start = time.time()
        result_frame_nsgaii = nsagii.solve(stocks, iter, mean_daily_returns, cov_matrix, days)
        time_nsga_solve = time.time() - start
        time_nsga.append(time_nsga_solve)
        LOG.info('nsgaii-%d - time: %s' % (iter, str(time_nsga_solve)))

        start = time.time()
        result_frame_nsgaiii = nsagii.solve_nsgaiii(stocks, iter, mean_daily_returns, cov_matrix, days)
        time_nsga_solve = time.time() - start
        time_nsgaiii.append(time_nsga_solve)
        LOG.info('nsagiii-%d - time: %s' % (iter, str(time_nsga_solve)))

        plt.subplot(131)
        max_sharpe_port_sm = result_frame_sm.iloc[result_frame_sm['sharpe'].idxmax()]
        sharpes_sm.append(max_sharpe_port_sm[2])
        plt.scatter(result_frame_sm.stdev, result_frame_sm.ret, c=result_frame_sm.sharpe, cmap='RdYlBu')
        plt.xlabel('stdev')
        plt.ylabel('ret')
        plt.scatter(max_sharpe_port_sm[1], max_sharpe_port_sm[0], marker=(3, 1, 0), color='r', s=300)
        LOG.info('sm-%d: \n %s' % (iter, str(max_sharpe_port_sm)))

        plt.subplot(132)
        max_sharpe_port_nsgaii = result_frame_nsgaii.iloc[result_frame_nsgaii['sharpe'].idxmax()]
        sharpes_nsga.append(max_sharpe_port_nsgaii[2])
        plt.scatter(result_frame_nsgaii.stdev, result_frame_nsgaii.ret, c=result_frame_nsgaii.sharpe, cmap='RdYlBu')
        plt.xlabel('stdev')
        plt.ylabel('ret')
        plt.scatter(max_sharpe_port_nsgaii[1], max_sharpe_port_nsgaii[0], marker=(5, 1, 0), color='r', s=300)
        LOG.info('nsgaii-%d: \n %s' % (iter, str(max_sharpe_port_nsgaii)))

        plt.subplot(133)
        max_sharpe_port_nsgaiii = result_frame_nsgaiii.iloc[result_frame_nsgaiii['sharpe'].idxmax()]
        sharpes_nsgaiii.append(max_sharpe_port_nsgaii[2])
        plt.scatter(result_frame_nsgaiii.stdev, result_frame_nsgaiii.ret, c=result_frame_nsgaiii.sharpe, cmap='RdYlBu')
        plt.xlabel('stdev')
        plt.ylabel('ret')
        plt.scatter(max_sharpe_port_nsgaiii[1], max_sharpe_port_nsgaiii[0], marker=(6, 2, 0), color='r', s=300)
        LOG.info('nsgaiii-%d: \n %s' % (iter, str(max_sharpe_port_nsgaiii)))

        LOG.info('%d / %d' % (num, len(iterations)))

    plt.figure('trend')
    plt.plot(iterations, sharpes_sm, label='sm')
    plt.plot(iterations, sharpes_nsga, label='nsgaii')
    plt.plot(iterations, sharpes_nsgaiii, label='nsgaii')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    plt.figure('time')
    plt.plot(iterations, time_sm, label='sm')
    plt.plot(iterations, time_nsga, label='nsgaii')
    plt.plot(iterations, time_nsgaiii, label='nsgaiii')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.show()
