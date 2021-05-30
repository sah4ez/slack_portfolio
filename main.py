#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""
import os
import sys
from os import environ as env
from bot import config
from bot.cmd import (
    help, welcome, solver, max_min, ga,
    analyze, meta, finam, find, price, tinvest_meta,
    tinvest
)
from bot.my_log import (get_logger)
import traceback


from telegram.ext import (Updater, CommandHandler, MessageHandler)
from telegram.ext.filters import Filters

LOG = get_logger("main")

TOKEN = env.get("TOKEN_BOT")
if TOKEN is None:
    TOKEN = sys.argv[1]
    LOG.info('Token is loaded: %s' % TOKEN is not None)

def error(update, context):
    LOG.warning('Update "%s" caused error "%s"' % (update, context.error))
    traceback.print_exc()

def main():
    updater = Updater(token=TOKEN) 
    dp = updater.dispatcher

    dp.add_handler(help.handler())
    dp.add_handler(welcome.handler())
    dp.add_handler(solver.handler())
    dp.add_handler(max_min.handler())
    dp.add_handler(ga.handler())
    dp.add_handler(analyze.handler())
    dp.add_handler(meta.handler())
    dp.add_handler(finam.handler())
    dp.add_handler(find.handler())
    dp.add_handler(price.handler())
    dp.add_handler(tinvest_meta.handler())
    dp.add_handler(tinvest.handler())

    dp.add_error_handler(error)

    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()
