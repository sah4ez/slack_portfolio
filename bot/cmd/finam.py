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
from telegram.ext import (CommandHandler)

def handler() -> CommandHandler:
    return CommandHandler(config.CMD_FINAM_CODE, cmd)

def cmd(update, context):
    msg = config.HELP_FINAM_CODE
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )
