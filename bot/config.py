CMD_PRICE = ["price", "цена", "price_p", "цена_п"]
RSP_PRICE = "%s (%s) - %.2f"
HELP_PRICE = format("*%s*[_p] (*%s*[_п]) _<имя_компании>_ - поиск цены акции на MOEX\n" % (CMD_PRICE[0], CMD_PRICE[1]))

CMD_CAPITAL = ["capital", "капитал", "capital_p", "капитал_п"]
RSP_CAPITAL = "%s : CAP %.2f : VOLUME %.2f : CAP/VOLUME %.2f"
HELP_CAPITAL = format(
    "*%s*[_p] (*%s*[_п]) _<имя_компании>_ - поиск капитализации, объема выпущенных акций"
    "и отношение капитализации к объему акций [_руб/акция_]\n" % (CMD_CAPITAL[0], CMD_CAPITAL[1]))

RSP_WAIT = "Подождите... Я уже ищу"
RSP_GA = "Я начал долгую оптимизацию... Когда я закончу, я вам сообщу. (ツ)"

CMD_UPDATE = ["update"]
CMD_UPDATE_P = ["update_p"]
CMD_DOWNLOAD_FILES = ["download"]
RSP_UPDATE_STOCK = "Загружены последнии версии файлов"
HELP_UPDATE = format(
    "*%s* (*%s*) _<имя_компании>_или *n* [%s] - обновить компнаию или первые n файлов, "
    "если указано *%s*, то будут загружены документы отчетности\n" %
    (CMD_UPDATE[0], CMD_UPDATE_P[0], CMD_DOWNLOAD_FILES[0], CMD_DOWNLOAD_FILES[0]))

RSP_NOF_FOUND_STOCK = "Не найдена акция %s...¯\_(ツ)_/¯"

CMD_MOEX = ["moex", "биржа", "moex_p", "биржа_п"]
HELP_MOEX = format("*%s*[_p] (*%s*[_п]) - получить ссылку акции на бирже\n" % (CMD_MOEX[0], CMD_MOEX[1]))

CMD_HELP = ["help", "помогите", "помощь"]

CMD_FILES = ["file", "файл", "files", "файлы"]
RSP_FILES = "Найдено %d файлов"
RSP_FILES_NOT_FOUND = "Я не нашел файлы... ¯\_(ツ)_/¯"
HELP_FILES = format("*%s*, *%s*, *%s*, *%s* [количество] _<имя_компании>_ - получить файлы раскрытия информации"
                    ", если количество не указано, то пришлет все найденные\n" %
                    (CMD_FILES[0], CMD_FILES[1], CMD_FILES[2], CMD_FILES[3]))

CMD_SELECT_FOR_PORTFOLIO = ["запомнить", "добавить", "add", "select", "запомнить_п", "добавить_п", "add_p", "select_p"]
RSP_SELECT_FOR_PORTFOLIO = "Добавлено в портфель %s | %s | %.2f: \n"
HELP_SELECT_FOR_PORTFOLIO = format(
    "*%s*[_п], *%s*[_п], *%s*[_p], *%s*[_p] _<имя_компании>_ - запомнить компанию для дальнейшей аналитики \n" %
    (CMD_SELECT_FOR_PORTFOLIO[0], CMD_SELECT_FOR_PORTFOLIO[1],
     CMD_SELECT_FOR_PORTFOLIO[2], CMD_SELECT_FOR_PORTFOLIO[3]))

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
    "*%s* (*%s*)  *%s* (*%s*) - загрузить история цен по месяцам для всех компаний\n" %
    (CMD_FINAM_CODE[0], CMD_FINAM_CODE[1], CMD_FINAM_CODE[0], CMD_FINAM_CODE[1],
     ARG_FINAM_CODE_ALL[0], ARG_FINAM_CODE_ALL[1]))

CMD_UPDATE_METAINFO = ["meta", "мета"]
RSP_UPDATE_METAINFO = "Справочная информация обновлена"
HELP_UPDATE_METAINFO = format("*%s* (*%s*) - обновить список компаний MOEX, free-float, capitalization\n" %
                              (CMD_UPDATE_METAINFO[0], CMD_UPDATE_METAINFO[1]))

CMD_ANALYSE = ["анализ", "analyse"]
RSP_ANALYSE = "Анализ пакате акций из команды selected"
HELP_ANALYSE = format("*%s* (*%s*) [_<trade_code>_] - проанализировать текущее состояние порфтеля "
                      "или выбарнных акции trade_code\n" % (CMD_ANALYSE[0], CMD_ANALYSE[1]))

CMD_MIN_MAX = ['max', 'min']
HELP_MAX = format(
    "*%s* _COUNT_ - посчитать первые COUNT портфель по максимальным/минимальным"
    " значениям стандартного отклонения за определенный период\n"
    % CMD_MIN_MAX[0])

CMD_GA_SIMPLE = ['ga']
HELP_GA_SIMPLE = format(
    '*%s* _COUNT_ - запустить расчет портфелей по простой реализации генетического алгоритма, для COUNT\n' %
    CMD_GA_SIMPLE[0])

CMD_NSGAII = ['nsgaii', 'nsgaiii']
HELP_NSGAII = format(
    '*%s* / *%s* _COUNT_ - запустить расчет порфелей по NSGA-II для COUNT\n' % (CMD_NSGAII[0], CMD_NSGAII[1]))

CMD_OPTIMIZE = ['optimize']
HELP_OPTIMIZE = format('*%s* TYPE_GA ITERATIONS [COUNT] [REPEAT] - запустить оптимизацию первых COUNT '
                       'портфелей за последние 12 часов с помощью алгоритма TYPE_GA '
                       'с количеством итераций ITERATIONS. REPEAT - сколько раз эту оптимизацию повторить\n' %
                       CMD_OPTIMIZE[0])

RSP_HELP = "Вот чему меня научили:\n" + HELP_PRICE + HELP_CAPITAL + \
           HELP_MOEX + HELP_UPDATE + HELP_FILES + \
           HELP_SELECT_FOR_PORTFOLIO + HELP_GET_LIST_SELECTED + HELP_FIND + \
           HELP_FINAM_CODE + HELP_UPDATE_METAINFO + HELP_ANALYSE + HELP_MAX + \
           HELP_GA_SIMPLE + HELP_NSGAII + HELP_OPTIMIZE

WELCOME = format("Привет, чтобы узнать что я умею напиши одно из @portfolio *%s*, *%s*, *%s*\n" %
                 (CMD_HELP[0], CMD_HELP[1], CMD_HELP[2]))

RSP_INVALID_PARAMETERS = 'Invalid parameters %s'
RSP_ERROR = "Ops... Some error."

LOG_FORMAT = "%(asctime)s |%(name)s:%(lineno)d|[%(levelname)s]: %(message)s"
LOG_ALL_FILE = "log/all.log"

GA_SIMPLE = "ga"
GA_NSGAII = "nsgaii"
GA_NSGAIII = "nsgaiii"
