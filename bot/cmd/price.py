#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""
import re
import yfinance as yf
from bot import config
from bot.my_log import get_logger
from telegram.ext import (MessageHandler)
from telegram.ext.filters import Filters

pattern = re.compile(config.CMD_PRICE)

LOG = get_logger('yahoo.price')

def handler():
    return MessageHandler(Filters.regex(config.CMD_PRICE), cmd)


def cmd(update, context):
    match = pattern.search(update.message.text)
    code = match.group(1)

    LOG.info('Get price for [%s]' % code)

    t = yf.Ticker(str(code).upper())
    data = t.history()

    last_quote = (data.tail(1)['Close'].iloc[0])
    msg = config.RSP_PRICE % (code, float(last_quote))

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )
