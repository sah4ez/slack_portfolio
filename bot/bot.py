import os
import sys
import threading
import time
import traceback
from os import environ as env

from bot.capital import capital
import bot.config as config
from bot.finam.finam import loader
from bot.finder import find
from bot.my_log import get_logger
from bot.select_for_portfolio import get_list_selected, select
from bot.sender_file import send_file
from bot.updater import update_metainfo, update
from bot.yahoo.price import price
from bot.analyse import analyser
from bot.analyse import solver, income_portfolio as ip
from bot.bot_impl.bot_api import Bot

LOG = get_logger("main")

# starterbot's ID as an environment variable
BOT_ID = env.get("BOT_ID")
TOKEN = env.get('SLACK_BOT_TOKEN')
if len(sys.argv) == 3:
    if TOKEN is None:
        TOKEN = sys.argv[1]
    if BOT_ID is None:
        BOT_ID = sys.argv[2]

bot = Bot(TOKEN=TOKEN, BOT_ID=BOT_ID)
# constants
AT_BOT = "<@" + str(bot.BOT_ID) + ">"

# instantiate Slack & Twilio clients
#slack_client = SlackClient(TOKEN)


def handle_command(command, channel, user):
    message = config.WELCOME
    words = str(command).split(' ')
    if words.__len__() < 1:
        response(channel, message)
        return
    if words[0] in config.CMD_HOSTNAME and len(words) >= 2:
        host = words[1]
        if host not in env.get("HOSTNAME"):
            LOG.warn("Can't run command %s for host %s on host %s" % (words[2], host, env.get("HOSTNAME")))
            return
        else:
            words.pop(0)
            words.pop(0)
    first_command = words[0]
    list_extracted_files = list()
    try:
        #  if first_command in config.CMD_HELP:
            #  response(channel, config.RSP_HELP)
        if first_command in config.CMD_HOSTNAME:
            hostname = env.get("HOSTNAME")
            response(channel, "ON HOST: %s" % hostname)

        elif first_command in config.CMD_PRICE:
            response(channel, config.RSP_WAIT)
            message = price(words)
            response(channel, message)
        elif first_command in config.CMD_CAPITAL:
            response(channel, config.RSP_WAIT)
            message = capital(words)
            response(channel, message)

        elif first_command in config.CMD_UPDATE or first_command in config.CMD_UPDATE_P:
            response(channel, config.RSP_WAIT)
            update(words)
            response(channel, config.RSP_UPDATE_STOCK)

        elif first_command in config.CMD_FILES:
            message, list_extracted_files = send_file(words)
            response(channel, message)
            for filename in list_extracted_files:
                bot.post_file(channel, filename)

        elif first_command in config.CMD_SELECT_FOR_PORTFOLIO:
            message = select(words)
            response(channel, message)

        elif first_command in config.CMD_GET_LIST_SELECTED:
            message = get_list_selected()
            response(channel, message)

        elif first_command in config.CMD_FIND:
            message = find(words)
            response(channel, message)

        elif first_command in config.CMD_FINAM_CODE:
            response(channel, config.RSP_WAIT)
            message = loader(words)
            response(channel, message)

        elif first_command in config.CMD_UPDATE_METAINFO:
            message = update_metainfo()
            response(channel, message)

        elif first_command in config.CMD_ANALYSE:
            message = analyser.analyse(words)
            response(channel, message)

        elif first_command in config.CMD_GA_SIMPLE:
            response(channel, config.RSP_GA)
            message = solver.ga(words)
            response(channel, message)

        elif first_command in config.CMD_NSGAII:
            response(channel, config.RSP_GA)
            message = solver.ga(words)
            response(channel, message)

        elif first_command in config.CMD_MIN_MAX:
            response(channel, config.RSP_GA)
            message = ip.for_portfolio(words)
            response(channel, message)

        elif first_command in config.CMD_OPTIMIZE:
            response(channel, config.RSP_GA)
            message = solver.optimize(words)
            response(channel, message)

        else:
            response(channel, message)

    except Exception:
        bot.reset_delay()
        LOG.error(config.RSP_ERROR + " %s" % words)
        traceback.print_exc(file=sys.stdout)
        message = traceback.format_exc().split('\n')[traceback.format_exc().split('\n').__len__() - 2]
        response(channel, config.RSP_ERROR + '\n' + message)
        for file in list_extracted_files:
            threading.Thread(os.remove(file)).start()


def response(to_channel, message):
    pass
#    bot.short_delay()
#    slack_client.api_call("chat.postMessage", channel=to_channel,
#                          text=message, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']
    return None, None, None


def parse_slack_wait(msg):
    pass
#   output_list = msg
#    if output_list and len(output_list) > 0:
#        for output in output_list:
#            if output and 'user' in output and bot.BOT_ID in output['user']:
#                if 'text' in output and (config.RSP_WAIT in output['text'] or config.RSP_GA in output['text']):
#                    bot.reset_delay()
#                    slack_client.api_call(
#                        method="chat.delete",
#                        channel=output['channel'],
#                        ts=output['ts'])


def welcome(msg):
    output_list = msg
    if output_list and len(output_list) > 0:
        for output in output_list:
            if 'text' in output and AT_BOT == output['text']:
                response(output['channel'], config.WELCOME)


#def listen():
#    try:
#        LOG.info("StarterBot connected and running!")
#        while True:
#            msg = slack_client.rtm_read()
#            # print(msg)
#            parse_slack_wait(msg)
#            welcome(msg)
#            command, channel, user = parse_slack_output(msg)
#            if command and channel and user:
#                handle_command(command, channel, user)
#                # with ProcessPoolExecutor(max_workers=env.get(THREAD)) as executor:
#                #     executor.submit(handle_command, command, channel)
#            time.sleep(bot.READ_WEBSOCKET_DELAY)
#    except Exception:
#        LOG.error('Exception on connect')
#        slack_client.rtm_connect()
#        traceback.print_exc(file=sys.stdout)
#        listen()
