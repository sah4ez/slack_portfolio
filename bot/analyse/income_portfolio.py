from datetime import datetime, timedelta
import config
from mongo import Portfolio as pf, mongo as db
import my_log
import texttable
import property

LOG = my_log.get_logger('income_portfolio')


def for_portfolio(words):
    if len(words) != 2:
        LOG.error('Ivalid parameters %s' % str(words))
        return config.RSP_INVALID_PARAMETERS

    position = int(words[1])
    is_max = True
    if words[0] == 'min':
        is_max = False

    LOG.info('Start calculate for %d' % position)
    profits = list()
    stdevs = list()
    table = texttable.Texttable(max_width=500)
    table.add_row(['id', 'profit', 'stdev'])
    for num, ordered in enumerate(
            pf.Portfolio.objects(date__gt=datetime(2017, 8, 8, 9, 0, 0, 0)).order_by('-max_item.sharpe_ratio')):
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
        try:
            part = float(stock.value)
            trade_code = str(stock.trade_code)
            stock_orm = db.stock_by_trade_code(trade_code)
            lot = int(stock_orm.lot)
            from_price = stock_orm.get_day_price(from_date)
            count = correct_on_lot(lot, part, money, from_price)

            stocks[stock_orm.trade_code] = str(count) + '|' + str(from_price)
            to_price = stock_orm.get_day_price(to_date) * (1 - property.ATON_TAX)
            income.append(float(count * to_price))
        except AttributeError:
            LOG.error('For stock %s not found attribute' % stock.trade_code)

    result = sum(income)
    LOG.info('Portfolio %s base price %s from %s to %s with price %s' % (stocks, money, from_date, to_date, result))
    return result


def correct_on_lot(lot, part, money, price):
    count = money * part * (1 - property.ATON_TAX) / price
    full = count // lot
    mod = count - (full * lot)
    if lot / 2 <= mod:
        full += 1
    return full * lot
