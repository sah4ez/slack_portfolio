import os, sys
import config, price

import time
import loader_from_file
from slackclient import SlackClient

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
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    if command.startswith(config.CMD_PRICE) or command.startswith(config.CMD_PRICE_RU):
        response = price.price(command)
    if command.startswith(config.CMD_CAPITAL) or command.startswith(config.CMD_CAPITAL_RU):
        response = capital.capital(command)
    if command.startswith("update"):
        loader_from_file.load_all()
        response = "Was uploaded"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            msg = slack_client.rtm_read()
            command, channel = parse_slack_output(msg)
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
