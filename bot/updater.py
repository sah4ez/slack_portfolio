import my_log
import loader_from_file as lfl
import re

LOG = my_log.get_logger('update')


def update(words):
    num = None

    if words.__len__() > 1 and re.compile(r'[0-9]').match(words[1]):
        num = int(words[1])

    lfl.load_stocks(num)
