import threading

import os
import requests

from bot.my_log import get_logger

LOG = get_logger("Bot")


class Bot:
    def __init__(self, TOKEN, BOT_ID):
        self.TOKEN = TOKEN
        self.READ_WEBSOCKET_DELAY = 1
        self.BOT_ID = BOT_ID

    def post_file(self, channels, filename, token=None):
        f = {'file': (filename, open(filename, 'rb'), 'application/octet-stream', {'Expires': '0'})}
        requests.post(url='https://slack.com/api/files.upload',
                      data={'token': token if token is not None else self.TOKEN, 'channels': channels, 'media': f},
                      headers={'Accept': 'application/json'}, files=f)
        LOG.info("Send file %s to channel: %s" % (filename, channels))
        rm = threading.Thread(os.remove(filename))
        rm.start()
        self.reset_delay()

    def reset_delay(self):
        self.READ_WEBSOCKET_DELAY = 1

    def short_delay(self):
        self.READ_WEBSOCKET_DELAY = 0.1
