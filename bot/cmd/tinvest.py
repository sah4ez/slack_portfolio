#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""

from bot import config
from telegram.ext import (CommandHandler)
from bot.finam.finam import history_all_stocks_tinvest

def handler() -> CommandHandler:
    return CommandHandler(config.CMD_TINVEST, cmd)

def cmd(update, context):
    msg = config.HELP_TINVEST
    history_all_stocks_tinvest()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )
