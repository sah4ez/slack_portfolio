import bot.mongo
import re

from bot.my_log import get_logger

LOG = get_logger('Parse_Portfolio')


def string_portfolios(path):
    LOG.info('Start for path=%s', path)
    str_file = ''
    with open(path, mode='r') as file:
        str_file = file.read()
        file.close()
    list_min_max = list()
    for line in str_file.split("=========="):
        list_min_max.append(line)

    for pair in list_min_max:
        pair_items = str(pair).split("----------")
        if len(pair_items) != 2:
            LOG.warn('Invalid parsed string: %s' % pair)
            continue
        max_item = pair_items[0]
        min_item = pair_items[1]
        portfolio = bot.mongo.Portfolio.Portfolio()
        max_portfolio = parse(max_item)
        min_portfolio = parse(min_item)

        portfolio.max_item = max_portfolio
        portfolio.min_item = min_portfolio
        portfolio.save()
        LOG.info('Save portfolio [max_r=%.4f max_std=%.4f max_s=%.4f][min_r=%.4f min_std=%.4f s=%.4f]',
                 portfolio.max_item.returns, portfolio.max_item.standard_deviation, portfolio.max_item.sharpe_ratio,
                 portfolio.min_item.returns, portfolio.min_item.standard_deviation, portfolio.min_item.sharpe_ratio)


def parse(string: str) -> bot.mongo.Portfolio.ItemPortfolio:
    float_pattern = re.compile('[0-9.-]{8,9}')
    stock_pattern = re.compile('^[A-Z]{4,5}.[A-Z]{2}')
    item_portfolio = bot.mongo.Portfolio.ItemPortfolio()
    for line in string.split('\n'):
        if line.startswith('ret'):
            item_portfolio.returns = float(float_pattern.search(line).group(0))
        if line.startswith('stdev'):
            item_portfolio.standard_deviation = float(float_pattern.search(line).group(0))
        if line.startswith('sharpe'):
            item_portfolio.sharpe_ratio = float(float_pattern.search(line).group(0))
        if stock_pattern.match(line):
            item = bot.mongo.Portfolio.Item()
            stock_trade_code = stock_pattern.search(line).group(0).split('.')
            item.trade_code = stock_trade_code[0]
            item.exchange = stock_trade_code[1]
            item.value = float(float_pattern.search(line).group(0))
            item_portfolio.stocks.append(item)

    return item_portfolio
