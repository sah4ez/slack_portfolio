#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""

from bot import config, property
from telegram.ext import (CommandHandler)
from bot.resources.loader import download_file
from bot.loader_from_file import load_stocks, load_all, update_stock_from_file

from pathlib import Path
Path("./res").mkdir(parents=True, exist_ok=True)

def handler() -> CommandHandler:
    return CommandHandler(config.CMD_UPDATE_METAINFO, cmd)

def cmd(update, context):
    msg = config.HELP_UPDATE_METAINFO
    download_file(property.URL_DATA, property.DATA)
    #  load_all()
    load_stocks(count=None, upload_files=True)
    #  update_stock_from_file()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )
