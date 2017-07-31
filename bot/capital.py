import config
import loader_from_file
import parser_command.command as p
import my_log

LOG = my_log.get_logger('capital')


def capital(words):
    name, privileged = p.name_and_priviledget(words)
    LOG.info('Get capital for [%s, %s]' % (name, str(privileged)))

    stock = loader_from_file.load_one_stock(name, privileged)

    if stock is None:
        return format(config.RSP_NOF_FOUND_STOCK % name)
    else:
        return format(config.RSP_CAPITAL % (
            stock.emitent_full_name,
            float(stock.capitalisation),
            float(stock.volume_stock_on_market),
            float(stock.capitalisation / stock.volume_stock_on_market)
        ))
