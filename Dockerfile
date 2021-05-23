FROM python:3.7

RUN mkdir -p -m 750 /home/bot/bot
WORKDIR /home/bot
ADD requirements.txt /home/bot
RUN apt-get install -y libbz2-dev
RUN python3.7 -m pip install --upgrade pip setuptools wheel

RUN pip3 install -r /home/bot/requirements.txt

ADD . /home/bot/

CMD [ "python", "/home/bot/main.py" ]
