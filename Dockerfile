FROM python:3.6

RUN mkdir -p -m 750 /home/bot/bot
WORKDIR /home/bot/bot
ADD requirements.txt /home/bot
ADD scripts /home/bot/

RUN pip3 install -r /home/bot/requirements.txt

ADD ./bot /home/bot/bot

# PhantomJS
ENV PHANTOMJS_VERSION 2.1.1
RUN wget --no-check-certificate -q -O - \
   https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 | tar xjC /opt &&\
   ln -s /opt/phantomjs-$PHANTOMJS_VERSION-linux-x86_64/bin/phantomjs /usr/bin/phantomjs &&\
   ln -s /opt/phantomjs-$PHANTOMJS_VERSION-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs

#CMD ["/bin/bash"]
CMD ['python3', '/home/bot/bot/bot.py', '${SLACK_BOT_TOKEN}', '${BOT_ID}']
