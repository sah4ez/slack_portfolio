FROM python:3.8

RUN mkdir -p -m 750 /home/bot/bot
WORKDIR /home/bot
ADD requirements.txt /home/bot

RUN pip3 install -r /home/bot/requirements.txt

ADD . /home/bot/

CMD [ "python", "/home/bot/main.py" ]
