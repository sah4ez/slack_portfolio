import os, sys

import capital
import config, price, url_board

import time
import loader_from_file
from slackclient import SlackClient
import logging

logging.basicConfig(level=logging.DEBUG)

LOG = logging.getLogger("__main__")

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
TOKEN = os.environ.get('SLACK_BOT_TOKEN')
if TOKEN is None:
    TOKEN = sys.argv[1]
if BOT_ID is None:
    BOT_ID = sys.argv[2]

# constants
AT_BOT = "<@" + str(BOT_ID) + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(TOKEN)


def handle_command(command, channel):
    message = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
              "* command with numbers, delimited by spaces."
    words = str(command).split(' ')
    if words.__len__() < 1:
        response(channel, message)
        return
    first_command = words[0]
    try:
        if first_command in config.CMD_HELP:
            response(channel, config.RSP_HELP)
        if first_command in config.CMD_PRICE:
            response(channel, config.RSP_WAIT)
            message = price.price(words)
            response(channel, message)
        if first_command in config.CMD_CAPITAL:
            response(channel, config.RSP_WAIT)
            message = capital.capital(words)
            response(channel, message)
        if first_command in config.CMD_MOEX:
            response(channel, config.RSP_WAIT)
            response(channel, url_board.get_url(words))
        if command.startswith(config.CMD_UPDATE):
            loader_from_file.load_all()
            response(channel, config.RSP_UPDATE_STOCK)
    except:
        LOG.error(config.RSP_ERROR + " %s" % words)
        response(channel, config.RSP_ERROR)


def response(to_channel, message):
    slack_client.api_call("chat.postMessage", channel=to_channel,
                          text=message, as_user=True)


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


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
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
    else:
        LOG.error("Connection failed. Invalid Slack token or bot ID?")
