FROM bot/base:1.0
ENV THREAD_SLACK=1
ADD ./bot /home/bot/bot

CMD ['python3', '/home/bot/bot/bot.py', '${SLACK_BOT_TOKEN}', '${BOT_ID}']
