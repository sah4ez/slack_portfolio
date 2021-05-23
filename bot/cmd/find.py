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
from bot import config

from telegram.ext import (MessageHandler)
from telegram.ext.filters import Filters

pattern = re.compile(config.CMD_FIND)

def handler() -> MessageHandler:
    return MessageHandler(Filters.regex(config.CMD_FIND), cmd)

def cmd(update, context):
    match = pattern.search(update.message.text)
    code = match.group(1)

    msg = config.RSP_FIND % code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )
