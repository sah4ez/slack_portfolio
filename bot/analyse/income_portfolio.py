from datetime import datetime, timedelta

import texttable

import config
import my_log
import property
from mongo import Portfolio as pf, mongo as db

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
    table.add_row(['id', 'price', 'profit', 'stdev'])
    for ordered in db.get_n_first_portfolios(position):
        item = ordered.max_item if is_max else ordered.min_item
        LOG.info('Predict for %s' % item)
        profit, correct_summ = predict(porftolio=item, money=100000)
        profits.append(profit)
        stdevs.append(ordered.max_item.standard_deviation)
        table.add_row([ordered._id, correct_summ, profit, ordered.max_item.standard_deviation])

    table.add_row(['', '', sum(profits) / len(profits), sum(stdevs) / len(stdevs)])
    return table.draw()


def predict(porftolio: pf.ItemPortfolio, money: int, from_date=(datetime.today() - timedelta(days=21)),
            to_date=datetime.today() - timedelta(days=1)):
    income = list()

    correct_summ = list()
    table = texttable.Texttable()
    table.add_row(['Code', 'SHORT', 'LOT', 'COUNT', 'COUNT_LOT', 'BASE_COUNT', 'PRICE', 'PART', 'FULL', 'INCOME'])
    for stock in porftolio.stocks:
        try:
            part = float(stock.value)
            trade_code = str(stock.trade_code)
            stock_orm = db.stock_by_trade_code(trade_code)
            lot = int(stock_orm.lot)
            from_price = load_price(stock_orm, from_date)
            count, before_correct_count, full = correct_on_lot(lot, part, money, from_price)
            correct_full_pirce = count * from_price
            correct_summ.append(correct_full_pirce)
            to_price = load_price(stock_orm, to_date)
            income.append(float(count * to_price))
            row = [stock_orm.trade_code, stock_orm.short_name, stock_orm.lot, count, full, before_correct_count,
                   from_price, part, count * from_price, to_price]
            table.add_row(row)
        except AttributeError:
            LOG.error('For stock %s not found attribute' % stock.trade_code)

    result = sum(income)
    print(table.draw())
    LOG.info('Portfolio base price %s (%s) from %s to %s with price %s' % (
        money, sum(correct_summ), from_date, to_date, result))
    return result, sum(correct_summ)


def load_price(stock_orm, date):
    load = False
    shift_days = 0
    while not load:
        try:
            from_price = stock_orm.get_day_price(date + timedelta(days=shift_days))
            return from_price
        except db.NotFoundPrice:
            load = False
            LOG.warn("Not found price %s on %s" % (stock_orm.trade_code, str(date + timedelta(days=shift_days))))
            if abs((date.date() - datetime.today().date()).days) <= 7:
                shift_days -= 1
            else:
                shift_days += 1
            if shift_days == 365:
                load = True


def correct_on_lot(lot, part, money, price):
    count = money * part * (1 - property.ATON_TAX) / price
    full = count // lot
    mod = count - (full * lot)
    if lot / 2 <= mod:
        full += 1
    return full * lot, count, full
