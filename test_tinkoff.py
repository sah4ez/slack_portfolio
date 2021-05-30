#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Alexandr Kozlenkov <sah4ez32@gmail.com>
#
# Distributed under terms of the MIT license.
"""
"""

import bot.tinvest_pkg.client as cli
import tinvest as ti
from datetime import datetime, timedelta

candels = cli.process_by_period_map('MVID', datetime.now() - timedelta(hours=7 * 24), datetime.now(), ti.CandleResolution.hour)
print(candels)

#  for x in cli.get_stocks():
    #  print(x)
