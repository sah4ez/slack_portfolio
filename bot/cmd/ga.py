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
from bot.analyse.solver import ga

pattern = re.compile(config.CMD_NSGAII)

def handler() -> MessageHandler:
    return MessageHandler(Filters.regex(config.CMD_NSGAII), cmd)

def cmd(update, context):
    msg = config.HELP_GA_SIMPLE

    match = pattern.search(update.message.text)

    if match.group(1) == "ga":
        print("ga", match.group(2))
    elif match.group(1) == "nsga2":
        print("nsga2", match.group(2))
    elif match.group(1) == "nsga3":
        print("nsga3", match.group(2))

    msg = ga([match.group(1), match.group(2)])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )
