## Virtual env

If you running bot in not conternized os (Docker), will be good create virtual evnieronment:

```bash
virtualenv portfolio
```

And install requirements:
```bash
pip install -r requirements.txt
```

## System environment

You need create file `.env` with variables:
```bash
BOT_ID=F83923YAS # get from bot/bot_print_id.py
SLACK_BOT_TOKEN=flkd-931284198453-mfdFsdfs3rsdsfsdfkjadsdl # get from settings you team
THREAD_SLACK=1
```

Next applay variable run script `./scripts/applay_env.sh`

## Change HOSTS

Run script `./scripts/connection_for_mongodb.sh` for add mongodb host.

# Docker

## Base image

First, build base image for bot:
```bash
docker build -t bot/base:1.0 -f Dockerfile.baseimage .
```

## Bot image
Build image for bot:
```bash
docker build -t kozlenkov.ru:5000/bot:1.0 -f Dockerfile .
```
or build and run:
```bash
docker-compose up --build -d
```
