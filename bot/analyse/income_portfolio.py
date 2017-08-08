from datetime import datetime, timedelta
import numpy as np
from mongo import Portfolio as pf, mongo as db
import my_log
import texttable

LOG = my_log.get_logger('income_portfolio')


def for_portfolio(position: int = 0, is_max=True):
    LOG.info('Start calculate for %d' % position)
    result = list()
    profits = list()
    stdevs = list()
    table = texttable.Texttable(max_width=500)
    table.add_row(['id', 'profit', 'stdev'])
    for num, ordered in enumerate(
            pf.Portfolio.objects(date__gt=datetime(2017, 8, 7, 19, 0, 0, 0)).order_by('-max_item.sharpe_ratio')):
        if num <= position:
            item = ordered.max_item if is_max else ordered.min_item
            LOG.info('Predict for %s' % item)
            profits.append(predict(porftolio=item, money=100000))
            stdevs.append(ordered.max_item.standard_deviation)
            table.add_row(
                [str(ordered._id), str(predict(porftolio=item, money=100000)),
                 str(ordered.max_item.standard_deviation)])

    table.add_row(['', sum(profits) / len(profits), sum(stdevs) / len(stdevs)])
    return table.draw()


def predict(porftolio: pf.ItemPortfolio, money: int, from_date=(datetime.today() - timedelta(days=43)),
            to_date=datetime.today() - timedelta(days=1)):
    db.connect()
    stocks = dict()
    income = list()

    for stock in porftolio.stocks:
        part = float(stock.value)
        trade_code = str(stock.trade_code)
        stock_orm = db.stock_by_trade_code(trade_code)
        from_price = stock_orm.get_day_price(from_date)
        count = (money * part) / from_price
        stocks[stock_orm.trade_code] = str(count) + '|' + str(from_price)
        to_price = stock_orm.get_day_price(to_date)
        income.append(float(count * to_price))
    result = sum(income)
    LOG.info('Portfolio %s base price %s from %s to %s with price %s' % (stocks, money, from_date, to_date, result))
    return result
