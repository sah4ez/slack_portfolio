import os
import sys
import threading
import time
import traceback

import analyse.nsga as nsga
import analyse.income_portfolio as ip
import requests
from slackclient import SlackClient

import capital
import config
import finam.finam as finam
import finder
import my_log
import select_for_portfolio
import sender_file
import updater
import url_board
import yahoo.price as price
from analyse import analyser
from parse import portfolio


LOG = my_log.get_logger("main")

# starterbot's ID as an environment variable
READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
BOT_ID = os.environ.get("BOT_ID")
TOKEN = os.environ.get('SLACK_BOT_TOKEN')
if TOKEN is None:
    TOKEN = sys.argv[1]
if BOT_ID is None:
    BOT_ID = sys.argv[2]

# constants
AT_BOT = "<@" + str(BOT_ID) + ">"

# instantiate Slack & Twilio clients
slack_client = SlackClient(TOKEN)


def handle_command(command, channel):
    global READ_WEBSOCKET_DELAY
    message = config.WELCOME
    words = str(command).split(' ')
    if words.__len__() < 1:
        response(channel, message)
        return
    first_command = words[0]
    list_extracted_files = list()
    try:
        if first_command in config.CMD_HELP:
            response(channel, config.RSP_HELP)

        elif first_command in config.CMD_PRICE:
            response(channel, config.RSP_WAIT)
            message = price.price(words)
            response(channel, message)
        elif first_command in config.CMD_CAPITAL:
            response(channel, config.RSP_WAIT)
            message = capital.capital(words)
            response(channel, message)

        elif first_command in config.CMD_MOEX:
            response(channel, config.RSP_WAIT)
            response(channel, url_board.get_url(words))

        elif first_command in config.CMD_UPDATE or first_command in config.CMD_UPDATE_P:
            response(channel, config.RSP_WAIT)
            updater.update(words)
            response(channel, config.RSP_UPDATE_STOCK)

        elif first_command in config.CMD_FILES:
            message, list_extracted_files = sender_file.send_file(words)
            response(channel, message)
            for filename in list_extracted_files:
                post_file(channel, filename)

        elif first_command in config.CMD_SELECT_FOR_PORTFOLIO:
            message = select_for_portfolio.select(words)
            response(channel, message)

        elif first_command in config.CMD_GET_LIST_SELECTED:
            message = select_for_portfolio.get_list_selected()
            response(channel, message)

        elif first_command in config.CMD_FIND:
            message = finder.find(words)
            response(channel, message)
        elif first_command in config.CMD_FINAM_CODE:
            response(channel, config.RSP_WAIT)
            message = finam.loader(words)
            response(channel, message)
        elif first_command in config.CMD_UPDATE_METAINFO:
            message = updater.update_metainfo()
            response(channel, message)
        elif first_command in config.CMD_ANALYSE:
            message = analyser.analyse(words)
            response(channel, message)
        elif first_command in ['ga']:
            nsga_ga = threading.Thread(nsga.ga(slack_client, channel))
            nsga_ga.start()
            response(channel, 'Finish GA!')
        elif first_command in ['storage_portfolio']:
            response(channel, config.RSP_WAIT)
            portfolio.string_portfolios(path='res/output.txt')
            response(channel, 'All portfolios saved')
        elif first_command in ['test']:
            response(channel, config.RSP_WAIT)
            message = ip.for_portfolio(int(words[1]))
            response(channel, message)
        else:
            response(channel, message)

    except Exception:
        reset_delay()
        LOG.error(config.RSP_ERROR + " %s" % words)
        traceback.print_exc(file=sys.stdout)
        message = traceback.format_exc().split('\n')[traceback.format_exc().split('\n').__len__() - 2]
        response(channel, config.RSP_ERROR + '\n' + message)
        for file in list_extracted_files:
            threading.Thread(os.remove(file)).start()


def response(to_channel, message):
    shor_delay()
    slack_client.api_call("chat.postMessage", channel=to_channel,
                          text=message, as_user=True)


def post_file(channels, filename):
    f = {'file': (filename, open(filename, 'rb'), 'application/octet-stream', {'Expires': '0'})}
    requests.post(url='https://slack.com/api/files.upload',
                  data={'token': TOKEN, 'channels': channels, 'media': f},
                  headers={'Accept': 'application/json'}, files=f)
    LOG.info("Send file %s to channel: %s" % (filename, channels))
    rm = threading.Thread(os.remove(filename))
    rm.start()
    reset_delay()


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


def parse_slack_wait(msg):
    output_list = msg
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'user' in output and BOT_ID in output['user']:
                if 'text' in output and config.RSP_WAIT in output['text']:
                    reset_delay()
                    slack_client.api_call(
                        method="chat.delete",
                        channel=output['channel'],
                        ts=output['ts'])


def welcome(msg):
    output_list = msg
    if output_list and len(output_list) > 0:
        for output in output_list:
            if 'text' in output and AT_BOT == output['text']:
                response(output['channel'], config.WELCOME)


def reset_delay():
    global READ_WEBSOCKET_DELAY
    READ_WEBSOCKET_DELAY = 1


def shor_delay():
    global READ_WEBSOCKET_DELAY
    READ_WEBSOCKET_DELAY = 0.1


def listen():
    try:
        LOG.info("StarterBot connected and running!")
        while True:
            msg = slack_client.rtm_read()
            # print(msg)
            parse_slack_wait(msg)
            welcome(msg)
            command, channel = parse_slack_output(msg)
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    except Exception:
        slack_client.rtm_connect()
        traceback.print_exc(file=sys.stdout)
        listen()


if __name__ == "__main__":

    if slack_client.rtm_connect():
        listen()
    else:
        LOG.error("Connection failed. Invalid Slack token or bot ID?")
