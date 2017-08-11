DATA = 'res/ListingSecurityList.csv'
URL_DATA = 'http://www.moex.com/ru/listing/securities-list-csv.aspx?type=2'

DATA_DESCRIPTION = 'res/description.xlsx'
URL_DATA_DESCRIPTION = 'http://fs.moex.com/f/6431/opisanie-poley.xlsx'

CAPITALIZATION = 'res/capitalization.html'
URL_CAPITALIZATION = 'http://www.moex.com/a4027/?print=1'

FREE_FLOAT = 'res/free-float.html'
URL_FREE_FLOAT = 'http://www.moex.com/ru/listing/free-float.aspx?print=1'

TYPE2_PATH = 'res/companies'
PORTAL = 'www.e-disclosure.ru'

TMP_EXTRACT = "tmp"

DOWNLOAD_URL_MATCH = 'FileLoad.ashx?Fileid='
DOWNLOAD_URL = 'e-disclosure.ru/portal/FileLoad.ashx?Fileid='
DOWNLOAD_SITE_DISCLOSURE = 'disclosure.skrin.ru'
DOWNLOAD_URL_DISCLOSURE = r'/docs/[0-9a-zA-Z]+/'

TYPE2 = '/type.html'
FILES = '/files.html'
FILES2 = '/files2.html'
FILES3 = '/files3.html'
FILES4 = '/files4.html'
FILES5 = '/files5.html'
ARCHIVES = '/archives'
HTTP_WWW = 'http://www.'

DISCLOSURE_ALL = '/?DTI=7'
DISCLOSURE_FIN = '/?DTI=8'
DISCLOSURE_CONSOLIDATION_FIN = '/?DTI=9'

BOARD = 'board.html'
URL_BOARD = 'http://www.moex.com/ru/issue.aspx?code='
SHORT_NAME_ATTR = 'Краткое наименование'

LAST_PRICE = "Цена последней сделки, рублей"
VOLUME_ON_MARKET = "Объем выпуска"

ZIP = r".zip$"
RAR = r".rar$"
SEVEN_Z = r".7z$"
PATH_PHANTOMJS = '/usr/local/bin/phantomjs'

SELECTED_STOCKS = 'res/selected.csv'
PRIVILEGED = r'^[a-zA-Z]{4}P$'
NOT_PRIVILEGED = r'^[a-zA-Z]{4}$'
PRIVILEGED_CMD = r'([a-zA-Z]+_p$|[а-яА-Я]+_п$)'
STOCKS = 'Акции'

DB_HOST = "mongodb"
DB_PORT = 27017
DB_COLLECT = 'stocks'

DB_CONTAINS_MORE_ONE = 'Found %d stocks[%s], should be one the stock. Specify the name company.'
DB_NOT_FOUNT_STOCK = 'Stock for [%s] not found'

FINAM_P_MONTH = '10'
FINAM_P_WEEK = '9'
FINAM_P_DAY = '8'
FINAM_P_HOUR = '7'

FINAM_SHIFT_MONTH = 365 * 5  # days
FINAM_SHIFT_WEEK = 7 * 50  # days
FINAM_SHIFT_DAY = 200  # days
FINAM_SHIFT_HOUR = 12 * 20  # hours
FINAM_PERIODS = [FINAM_P_MONTH, FINAM_P_WEEK, FINAM_P_DAY, FINAM_P_HOUR]

ATON_TAX = 0.22 / 100  # 18 % percent of buy/sell

PORTFOLION_STOCK = r'[A-Z]'
LOT_STOCK = r'<th>Размер лота</th><td>[0-9 ]+</td>'
SHORT_NAME_STOCK = r'<th>Краткое наименование</th><td>[a-zA-Zа-яА-Я0-9 +\-_\'."]+</td>'
