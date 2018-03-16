DJANGO_SETTINGS_MODULE:=colombe.settings.local

run-server:
	colombe --settings ${DJANGO_SETTINGS_MODULE} django runserver

run-worker:
	colombe --settings ${DJANGO_SETTINGS_MODULE} run worker

shell:
	colombe --settings ${DJANGO_SETTINGS_MODULE} django shell_plus

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down