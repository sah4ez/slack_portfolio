import loader_from_file
import parser_command.command as p


def get_url(words):
    company, privileged = p.name_and_priviledget(words)
    stock = loader_from_file.load_one_stock(company, privileged)
    return loader_from_file.url_board(stock.trade_code)


