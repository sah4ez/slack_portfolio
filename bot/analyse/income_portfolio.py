from datetime import datetime, timedelta

from mongo import Portfolio as pf, mongo as db
import my_log

LOG = my_log.get_logger('income_portfolio')


def for_portfolio(position: int = 0):
    LOG.info('Start calculate for %d' % position)
    for num, ordered in enumerate(pf.Portfolio.objects.order_by('-max_item.sharpe_ratio')):
        if num == position:
            LOG.info('Predict for %s' % ordered)
            return predict(porftolio=ordered, money=100000)


def predict(porftolio: pf.Portfolio, money: int, from_date=(datetime.today() - timedelta(days=43)),
            to_date=datetime.today() - timedelta(days=14)):
    db.connect()
    stocks = dict()
    income = list()

    for stock in porftolio.max_item.stocks:
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
