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
import bot.tinvest_pkg.client as cli
from bot.loader_from_file import load_stocks_tinvest

from telegram.ext import (CommandHandler)
from bot import config

pattern = re.compile(config.CMD_T_META)


def handler() -> CommandHandler:
    return CommandHandler(config.CMD_T_META, cmd)


def cmd(update, context):
    msg = config.CMD_T_META
    stocks = cli.load_stocks()
    for n, i in enumerate(stocks):
        print(n, i)
        print()
    load_stocks_tinvest(stocks)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )
