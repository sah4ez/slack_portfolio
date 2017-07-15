import config


def company_price(command):
    company = ""
    if command.startswith(config.CMD_PRICE):
        company = command.split(config.CMD_PRICE)[1].strip().lower()
    if command.startswith(config.CMD_PRICE_RU):
        company = command.split(config.CMD_PRICE_RU)[1].strip().lower()
    return company


def company_capital(command):
    company = ""
    if command.startswith(config.CMD_CAPITAL):
        company = command.split(config.CMD_CAPITAL)[1].strip().lower()
    if command.startswith(config.CMD_CAPITAL_RU):
        company = command.split(config.CMD_CAPITAL_RU)[1].strip().lower()
    return company
