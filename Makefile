NAME=investment_bot

build:
	docker build -t ${NAME} -f Dockerfile .

run:
	docker run --rm --name ${NAME} -it -e TOKEN_BOT=${TOKEN_BOT} ${NAME}

run-dev:
	docker run --rm \
		-v $(shell pwd):/home/bot \
		--name ${NAME} \
		-it \
		-e TOKEN_BOT=${TOKEN_BOT} \
		-e DB_NAME_ENV=portfolio \
		-e DB_HOST=194.113.104.149 \
		-e DB_PORT=27017 \
		-e DB_USERNAME=user \
		-e DB_PASSWORD=${DB_PASSWORD} \
		${NAME}
