#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""
import time
import re
from bot import config

from telegram.ext import (MessageHandler)
from telegram.ext.filters import Filters

pattern = re.compile(config.CMD_OPTIMIZE)

def handler() -> MessageHandler:
    return MessageHandler(Filters.regex(config.CMD_OPTIMIZE), cmd)

def cmd(update, context):
    msg = config.RSP_GA
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )

    match = pattern.search(update.message.text)
    print(match.group(1))
    print(match.group(2))
    print(match.group(3))

    time.sleep(1)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="типа закончил :-)",
    )
