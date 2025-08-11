.PHONY: up down build deploy delete

up:
	docker-compose up -d

down:
	docker-compose down

build:
	sam build

deploy:
	sam deploy --guided

delete:
	sam delete
