import os
import sys
from slackclient import SlackClient

BOT_NAME = 'portfolio'

TOKEN = os.environ.get('SLACK_BOT_TOKEN')
BOT_ID = os.environ.get('BOT_ID')

if __name__ == "__main__":
    if TOKEN is None:
        TOKEN = sys.argv[1]
    if BOT_ID is None:
        BOT_ID = sys.argv[2]

    slack_client = SlackClient(sys.argv[1])
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)
