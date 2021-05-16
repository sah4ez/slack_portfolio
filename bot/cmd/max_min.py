#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""

from bot import config
import re

from telegram.ext import (MessageHandler)
from telegram.ext.filters import Filters
from bot.analyse import income_portfolio

pattern = re.compile(config.CMD_MIN_MAX)


def handler() -> MessageHandler:
    return MessageHandler(Filters.regex(config.CMD_MIN_MAX), cmd)


def cmd(update, context):
    msg = config.HELP_NSGAII
    match = pattern.search(update.message.text)

    msg = income_portfolio.for_portfolio([match.group(1), match.group(2)])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='```\n'+msg+'\n```',
        parse_mode='MarkdownV2',
    )
