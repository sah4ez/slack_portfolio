CMD_PRICE_P = ["price_p", "цена_п"]
RSP_PRICE_P = "%s (%s) - %.2f"
HELP_PRICE_P = format(
    "*%s* (*%s*) _<имя_компании>_ - поиск цены привелигированной акции на MOEX\n" % (CMD_PRICE_P[0], CMD_PRICE_P[1]))

CMD_PRICE = ["price", "цена"]
RSP_PRICE = "%s (%s) - %.2f"
HELP_PRICE = format("*%s* (*%s*) _<имя_компании>_ - поиск цены акции на MOEX\n" % (CMD_PRICE[0], CMD_PRICE[1]))

CMD_CAPITAL_P = ["capital_p", "капитал_п"]
RSP_CAPITAL_P = "%s : CAP %.2f : VOLUME %.2f : CAP/VOLUME %.2f"
HELP_CAPITAL_P = format(
    "*%s* (*%s*) _<имя_компании>_ - поиск капитализации, объема выпущенных привелигированных акций"
    "и отношение капитализации к объему акций [_руб/акция_]\n" % (CMD_CAPITAL_P[0], CMD_CAPITAL_P[1]))

CMD_CAPITAL = ["capital", "капитал"]
RSP_CAPITAL = "%s : CAP %.2f : VOLUME %.2f : CAP/VOLUME %.2f"
HELP_CAPITAL = format(
    "*%s* (*%s*) _<имя_компании>_ - поиск капитализации, объема выпущенных акций"
    "и отношение капитализации к объему акций [_руб/акция_]\n" % (CMD_CAPITAL[0], CMD_CAPITAL[1]))

RSP_WAIT = "Подождите... Я уже ищу"

CMD_UPDATE = ["update"]
CMD_UPDATE_P = ["update_p"]
CMD_DOWNLOAD_FILES = ["download"]
RSP_UPDATE_STOCK = "Загружены последнии версии файлов"
HELP_UPDATE = format(
    "*%s* (*%s*) _<имя_компании>_или *n* [%s] - обновить компнаию или первые n файлов, "
    "если указано *%s*, то будут загружены документы отчетности\n" %
    (CMD_UPDATE[0], CMD_UPDATE_P[0], CMD_DOWNLOAD_FILES[0], CMD_DOWNLOAD_FILES[0]))

RSP_NOF_FOUND_STOCK = "Не найдена акция %s...¯\_(ツ)_/¯"
RSP_NOF_FOUND_STOCK_P = "Не найдена привелигированная акция %s...¯\_(ツ)_/¯"

CMD_MOEX_P = ["moex_p", "биржа_п"]
HELP_MOEX_P = format(
    "*%s* (*%s*) - получить ссылку привелигированной акции на бирже\n" % (CMD_MOEX_P[0], CMD_MOEX_P[1]))

CMD_MOEX = ["moex", "биржа"]
HELP_MOEX = format("*%s* (*%s*) - получить ссылку акции на бирже\n" % (CMD_MOEX[0], CMD_MOEX[1]))

CMD_HELP = ["help", "помогите", "помощь"]

CMD_FILES = ["file", "файл", "files", "файлы"]
RSP_FILES = "Найдено %d файлов"
RSP_FILES_NOT_FOUND = "Я не нашел файлы... ¯\_(ツ)_/¯"
HELP_FILES = format("*%s*, *%s*, *%s*, *%s* [количество] _<имя_компании>_ - получить файлы раскрытия информации"
                    ", если количество не указано, то пришлет все найденные\n" %
                    (CMD_FILES[0], CMD_FILES[1], CMD_FILES[2], CMD_FILES[3]))

CMD_SELECT_FOR_PORTFOLIO_P = ["запомнить_п", "добавить_п", "add_p", "select_p"]
CMD_SELECT_FOR_PORTFOLIO = ["запомнить", "добавить", "add", "select"]
RSP_SELECT_FOR_PORTFOLIO = "Добавлено в портфель %s | %s | %.2f: \n"
HELP_SELECT_FOR_PORTFOLIO = format(
    "*%s*, *%s*, *%s*, *%s* _<имя_компании>_ - запомнить компанию для дальнейшей аналитики \n" %
    (CMD_SELECT_FOR_PORTFOLIO[0], CMD_SELECT_FOR_PORTFOLIO[1],
     CMD_SELECT_FOR_PORTFOLIO[2], CMD_SELECT_FOR_PORTFOLIO[3]))
HELP_SELECT_FOR_PORTFOLIO_P = format(
    "*%s*, *%s*, *%s*, *%s* _<имя_компании>_ - запомнить компанию для дальнейшей аналитики \n" %
    (CMD_SELECT_FOR_PORTFOLIO_P[0], CMD_SELECT_FOR_PORTFOLIO_P[1],
     CMD_SELECT_FOR_PORTFOLIO_P[2], CMD_SELECT_FOR_PORTFOLIO_P[3]))

CMD_GET_LIST_SELECTED = ["selected", "выбранные"]
RSP_GET_LIST_SELECTED = "Вот запомненные компании: \n %s"
HELP_GET_LIST_SELECTED = format(
    "*%s*, *%s* - выведет список запомненных компаний \n" % (CMD_GET_LIST_SELECTED[0], CMD_GET_LIST_SELECTED[1]))

CMD_FIND = ["find", "найти"]
RSP_FIND = "Найдено: %s\n"
RSP_NOT_FOUND = "Я ничего не нашел... ¯\_(ツ)_/¯"
HELP_FIND = format("*%s*, *%s* _<имя_компании>_ - вернет список компаний, имена которых содеражать _<имя_компании>_\n" %
                   (CMD_FIND[0], CMD_FIND[1]))

CMD_FINAM_CODE = ["finam", "финам"]
ARG_FINAM_CODE_ALL = ["all", "все"]
RSP_FINAM_CODE = "Для %s с финам кодом %s обновлена история"
RSP_FINAM_CODE_ALL = "Все акции обновлены"
HELP_FINAM_CODE = format(
    "*%s* (*%s*) _<код_с_биржи>_ - загрузить историю по месяцам для _<код_с_биржи>_ (ex.: ALFT) или \n "
    "*%s* (*%s*)  *%s* (*%s*) - загрузить история цен по месяцам для всех компаний" %
    (CMD_FINAM_CODE[0], CMD_FINAM_CODE[1], CMD_FINAM_CODE[0], CMD_FINAM_CODE[1],
     ARG_FINAM_CODE_ALL[0], ARG_FINAM_CODE_ALL[1]))

CMD_UPDATE_METAINFO = ["meta", "мета"]
RSP_UPDATE_METAINFO = "Справочная информация обновлена"
HELP_UPDATE_METAINFO = format("*%s* (*%s) - обновить список компаний MOEX, free-float, capitalization\n" %
                              (CMD_UPDATE_METAINFO[0], CMD_UPDATE_METAINFO[1]))

CMD_ANALYSE = ["анализ", "analyse"]
RSP_ANALYSE = "Анализ пакате акций из команды selected"
HELP_ANALYSE = format("*%s* (*%s*) [_<trade_code>_] - проанализировать текущее состояние порфтеля "
                      "или выбарнных акции trade_code\n" % (CMD_ANALYSE[0], CMD_ANALYSE[1]))

RSP_HELP = "Вот чему меня научили:\n" + HELP_PRICE + HELP_PRICE_P + HELP_CAPITAL + HELP_CAPITAL_P + \
           HELP_MOEX + HELP_MOEX_P + \
           HELP_UPDATE + HELP_FILES + \
           HELP_SELECT_FOR_PORTFOLIO + HELP_SELECT_FOR_PORTFOLIO_P + \
           HELP_GET_LIST_SELECTED + HELP_FIND + HELP_FINAM_CODE + HELP_UPDATE_METAINFO + \
           HELP_ANALYSE

WELCOME = format("Привет, чтобы узнать что я умею напиши одно из @portfolio *%s*, *%s*, *%s*\n" %
                 (CMD_HELP[0], CMD_HELP[1], CMD_HELP[2]))

RSP_ERROR = "Ops... Some error."

LOG_FORMAT = "%(asctime)s |%(name)s:%(lineno)d|[%(levelname)s]: %(message)s"
LOG_ALL_FILE = "log/all.log"
