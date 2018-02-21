DJANGO_SETTINGS_MODULE:=holyter.settings.local

run-server:
	holyter django runserver

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down