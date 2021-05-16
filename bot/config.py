CMD_PRICE = r"price (\w+)"
RSP_PRICE = "%s - %.2f"
HELP_PRICE = format("%s _<имя_компании>_ - поиск цены акции на MOEX\n" % (CMD_PRICE[0]))

CMD_CAPITAL = ["capital", "капитал", "capital_p", "капитал_п"]
RSP_CAPITAL = "%s : CAP %.2f : VOLUME %.2f : CAP/VOLUME %.2f"
HELP_CAPITAL = format(
    "%s[_p] (%s[_п]) _<имя_компании>_ - поиск капитализации, объема выпущенных акций"
    "и отношение капитализации к объему акций [_руб/акция_]\n" % (CMD_CAPITAL[0], CMD_CAPITAL[1]))

RSP_WAIT = "Подождите... Я уже ищу"
RSP_GA = "Я начал долгую оптимизацию... Когда я закончу, я вам сообщу. (ツ)"

CMD_UPDATE = ["update"]
CMD_UPDATE_P = ["update_p"]
CMD_DOWNLOAD_FILES = ["download"]
RSP_UPDATE_STOCK = "Загружены последнии версии файлов"
HELP_UPDATE = format(
    "%s (%s) _<имя_компании>_или n [%s] - обновить компнаию или первые n файлов, "
    "если указано %s, то будут загружены документы отчетности\n" %
    (CMD_UPDATE[0], CMD_UPDATE_P[0], CMD_DOWNLOAD_FILES[0], CMD_DOWNLOAD_FILES[0]))

RSP_NOF_FOUND_STOCK = "Не найдена акция %s...¯\_(ツ)_/¯"

CMD_HELP = "help"
CMD_START = "start"

CMD_FILES = ["file", "файл", "files", "файлы"]
RSP_FILES = "Найдено %d файлов"
RSP_FILES_NOT_FOUND = "Я не нашел файлы... ¯\_(ツ)_/¯"
HELP_FILES = format("%s, %s, %s, %s [количество] _<имя_компании>_ - получить файлы раскрытия информации"
                    ", если количество не указано, то пришлет все найденные\n" %
                    (CMD_FILES[0], CMD_FILES[1], CMD_FILES[2], CMD_FILES[3]))

CMD_SELECT_FOR_PORTFOLIO = ["запомнить", "добавить", "add", "select", "запомнить_п", "добавить_п", "add_p", "select_p"]
RSP_SELECT_FOR_PORTFOLIO = "Добавлено в портфель %s | %s | %.2f: \n"
HELP_SELECT_FOR_PORTFOLIO = format(
    "%s[_п], %s[_п], %s[_p], %s[_p] _<имя_компании>_ - запомнить компанию для дальнейшей аналитики \n" %
    (CMD_SELECT_FOR_PORTFOLIO[0], CMD_SELECT_FOR_PORTFOLIO[1],
     CMD_SELECT_FOR_PORTFOLIO[2], CMD_SELECT_FOR_PORTFOLIO[3]))

CMD_GET_LIST_SELECTED = ["selected", "выбранные"]
RSP_GET_LIST_SELECTED = "Вот запомненные компании: \n %s"
HELP_GET_LIST_SELECTED = format(
    "%s, %s - выведет список запомненных компаний \n" % (CMD_GET_LIST_SELECTED[0], CMD_GET_LIST_SELECTED[1]))

CMD_FIND = r"find (\w+)"
RSP_FIND = "Найдено: %s\n"
RSP_NOT_FOUND = "Я ничего не нашел... ¯\_(ツ)_/¯"
HELP_FIND = format("%s _<имя_компании>_ - вернет список компаний, имена которых содеражать _<имя_компании>_\n" %
                   (CMD_FIND))

CMD_FINAM_CODE = "finam"
ARG_FINAM_CODE_ALL = ["all", "все"]
RSP_FINAM_CODE = "Для %s с финам кодом %s обновлена история"
RSP_FINAM_CODE_ALL = "Все акции обновлены"
HELP_FINAM_CODE = format(
    "%s _<код_с_биржи>_ - загрузить историю по месяцам для _<код_с_биржи>_ (ex.: ALFT) или \n "
    "%s - загрузить историю цен по месяцам для всех компаний\n" %
    (CMD_FINAM_CODE, CMD_FINAM_CODE))

CMD_UPDATE_METAINFO = "meta"
RSP_UPDATE_METAINFO = "Справочная информация обновлена"
HELP_UPDATE_METAINFO = format("%s - обновить список компаний MOEX, free-float, capitalization\n" %
                              (CMD_UPDATE_METAINFO))

CMD_ANALYSE = "analyze"
RSP_ANALYSE = "Анализ пакате акций из команды selected"
HELP_ANALYSE = format("%s [_<trade_code>_] - проанализировать текущее состояние порфтеля "
                      "или выбарнных акции trade_code\n" % (CMD_ANALYSE))

CMD_MIN_MAX = r'(max|min)\s(\d+)'
HELP_MAX = format(
    "%s _COUNT_ - посчитать первые COUNT портфель по максимальным/минимальным"
    " значениям стандартного отклонения за определенный период\n"
    % CMD_MIN_MAX)

CMD_GA_SIMPLE = 'ga\s(\d+)'
HELP_GA_SIMPLE = format(
    '%s _COUNT_ - запустить расчет портфелей по простой реализации генетического алгоритма, для COUNT\n' %
    CMD_GA_SIMPLE)

CMD_NSGAII = r'(ga|nsgaii|nsgaiii)\s(\d+)'
HELP_NSGAII = format(
    '%s _COUNT_ - запустить расчет порфелей по NSGA-II для COUNT\n' % CMD_NSGAII)

CMD_OPTIMIZE = r'optimize\s(nsga2|nsga3)\s(\d+)\s(\d+)'
HELP_OPTIMIZE = format('%s TYPE_GA ITERATIONS [COUNT] [REPEAT] - запустить оптимизацию первых COUNT '
                       'портфелей за последние 12 часов с помощью алгоритма TYPE_GA '
                       'с количеством итераций ITERATIONS. REPEAT - сколько раз эту оптимизацию повторить\n' %
                       CMD_OPTIMIZE)

SAVED_PORTFOLIO = ["pf", "list", "select", "current", "save", "add", "rm", "delete", "stat", "compare"]
HELP_SAVED_PORTFOLIO = format("\n%s [COMMAND] [ARGS] \n"
                              "COMMAND: \n"
                              "    %s - список всех выбранных потрфелей\n"
                              "    %s NAME - выбрать текущим потрфель с именем NAME\n"
                              "    %s - текущий портфель\n"
                              "    %s ID NAME - сохранить портфель с ID под именем NAME\n"
                              "    %s STOCK LOT PRICE - добавить в текущий портфель лотов LOT акции STOCK по цене PRICE\n"
                              "    %s STOCK LOT - удалить в текущем портфеле лоты LOT акции STOCK\n"
                              "    %s NAME - удалить портфель с названием NAME\n"
                              "    %s - просчитать текущий портфель\n"
                              "    %s NAME - сравнить текущий портфель с портфелем NAME\n"
                              % (SAVED_PORTFOLIO[0], SAVED_PORTFOLIO[1], SAVED_PORTFOLIO[2],
                                 SAVED_PORTFOLIO[3], SAVED_PORTFOLIO[4], SAVED_PORTFOLIO[5],
                                 SAVED_PORTFOLIO[6], SAVED_PORTFOLIO[7], SAVED_PORTFOLIO[8],
                                 SAVED_PORTFOLIO[9]))

CMD_HOSTNAME = ["host"]
HELP_HOSTNAME = format(
    "%s HOSTNAME - если бот запущен в нескольких экземплярах, то используейте "
    "эту команду для запуска на конкретном экземеляре HOSTNAME\b" % (
        CMD_HOSTNAME[0]))

RSP_HELP = "Вот чему меня научили:\n" + HELP_HOSTNAME + HELP_PRICE + HELP_CAPITAL + \
           HELP_UPDATE + HELP_FILES + \
           HELP_SELECT_FOR_PORTFOLIO + HELP_GET_LIST_SELECTED + HELP_FIND + \
           HELP_FINAM_CODE + HELP_UPDATE_METAINFO + HELP_ANALYSE + HELP_MAX + \
           HELP_GA_SIMPLE + HELP_NSGAII + HELP_OPTIMIZE + HELP_SAVED_PORTFOLIO

WELCOME = "Привет, чтобы узнать что я умею напиши /help"

RSP_INVALID_PARAMETERS = 'Invalid parameters %s'
RSP_ERROR = "Ops... Some error."

LOG_FORMAT = "%(asctime)s |%(name)s:%(lineno)d|[%(levelname)s]: %(message)s"
LOG_ALL_FILE = "log/all.log"

GA_SIMPLE = "ga"
GA_NSGAII = "nsgaii"
GA_NSGAIII = "nsgaiii"
