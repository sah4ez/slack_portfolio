import matplotlib.pyplot as plt
import my_log
from mongo import mongo as db
from analyse import solver, nsga as sm, nsga_platypus as nsagii
import time

LOG = my_log.get_logger('compare-solver')

db.connect()

iterations = [10000, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000]
# iterations = [10000, 50000]
sharpes_sm = list()
sharpes_nsga = list()
time_sm = list()
time_nsga = list()

trade_codes = ["SBER", "TUCH", "ROST", "TGKDP", "OPIN", "RUAL", "MSNG", "MRKS", "DVEC", "GCHE", "TRMK", "AKRN", "OPIN",
               "IRKT", "UWGN"]

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
    LOG.info('sm-%d - time: %s' % (iter, str(time_nsga_solve)))

    plt.subplot(121)
    max_sharpe_port_sm = result_frame_sm.iloc[result_frame_sm['sharpe'].idxmax()]
    sharpes_sm.append(max_sharpe_port_sm[2])
    plt.scatter(result_frame_sm.stdev, result_frame_sm.ret, c=result_frame_sm.sharpe, cmap='RdYlBu')
    plt.xlabel('stdev')
    plt.ylabel('ret')
    plt.scatter(max_sharpe_port_sm[1], max_sharpe_port_sm[0], marker=(3, 1, 0), color='r', s=300)
    LOG.info('sm-%d: \n %s' % (iter, str(max_sharpe_port_sm)))

    plt.subplot(122)
    max_sharpe_port_nsgaii = result_frame_nsgaii.iloc[result_frame_nsgaii['sharpe'].idxmax()]
    sharpes_nsga.append(max_sharpe_port_nsgaii[2])
    plt.scatter(result_frame_nsgaii.stdev, result_frame_nsgaii.ret, c=result_frame_nsgaii.sharpe, cmap='RdYlBu')
    plt.xlabel('stdev')
    plt.ylabel('ret')
    plt.scatter(max_sharpe_port_nsgaii[1], max_sharpe_port_nsgaii[0], marker=(5, 1, 0), color='r', s=300)
    LOG.info('nsgaii-%d: \n %s' % (iter, str(max_sharpe_port_nsgaii)))

    LOG.info('%d / %d' % (num, len(iterations)))

plt.figure('trend')
plt.plot(iterations, sharpes_sm, label='sm')
plt.plot(iterations, sharpes_nsga, label='nsgaii')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

plt.figure('time')
plt.plot(iterations, time_sm, label='sm')
plt.plot(iterations, time_nsga, label='nsgaii')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
plt.show()
