DJANGO_SETTINGS_MODULE:=colombe.settings.local

run-server:
	colombe --settings ${DJANGO_SETTINGS_MODULE} django runserver

shell:
	colombe --settings ${DJANGO_SETTINGS_MODULE} django shell

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down