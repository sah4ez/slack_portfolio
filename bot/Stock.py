from bot.extractor import get_free_float, get_value_capitalization


# from ..database import db_property as prop


class Stock:
    datestamp = ''
    instrument_id = 0
    list_section = 0
    rn = ''
    supertype = 0
    instrument_type = 0
    instrument_category = 0
    trade_code = 0
    isin = 0
    registry_number = 0
    registry_date = 0
    emitent_full_name = 0
    inn = 0
    nominal = 0
    currency = 0
    security_has_default = 0
    security_has_tech_default = 0
    capitalisation = 0.0
    free_float = 0.0
    official_url = ''
    url = ''
    files_name = []
    short_name = ''
    finame_em = 0
    last_price = 0.0
    volume_stock_on_market = 0

    def stock_line(self, line):
        self.datestamp = line[0]
        self.currency = line[14]
        self.trade_code = line[7]
        self.emitent_full_name = line[11]
        self.capitalisation = float(get_value_capitalization(self.trade_code))
        self.free_float = float(get_free_float(self.trade_code))
        self.official_url = line[37]
        self.url = line[38]
        return self

        # def from_doc(self, doc):
        #     self.datestamp = doc[prop.S_DATE]
        #     self.trade_code = doc[prop.S_TRADE_CODE]
        #     self.emitent_full_name = doc[prop.S_NAME]
        #     self.capitalisation = doc[prop.S_CAPITALIZATION]
        #     self.free_float = doc[prop.S_FREE_FLOAT]
        #     self.files_name = doc[prop.S_FILES_NAME]
        #     self.finame_em = doc[prop.S_FINAM_EM]
        #     self.short_name = doc[prop.S_SHORT_NAME]
        #     return self
