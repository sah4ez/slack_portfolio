NAME=investment_bot

build:
	docker build -t ${NAME} -f Dockerfile .

run:
	docker run --rm --name ${NAME} -it -e TOKEN_BOT=${TOKEN_BOT} ${NAME}
