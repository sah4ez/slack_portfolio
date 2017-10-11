FROM bot/base:1.0
ENV THREAD_SLACK=1
ADD ./bot /home/bot/bot
RUN echo "185.118.67.195 mongodb" >> /etc/hosts

CMD ['python3', '/home/bot/bot/bot.py', '${SLACK_BOT_TOKEN}', '${BOT_ID}']
