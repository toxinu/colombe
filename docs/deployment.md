# Deployment

## Ubuntu

```
# Requirements
$ apt-get install nginx redis-server rabbitmq-server postgresql python3-pip
$ adduser --shell=/bin/false --no-create-home --disabled-password colombe
$ mkdir /srv/colombe
$ cd /srv/colombe
$ pip3 install pip --upgrade
$ pip3 install virtualenv
$ virtualenv .venv -p python3

# Install postgres
$ sudo -u postgres psql
postgres=# CREATE DATABASE colombe WITH PASSWORD 'password';;
postgres=# ALTER ROLE colombe SET client_encoding TO 'utf8';
postgres=# ALTER ROLE colombe SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE colombe SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE colombe TO colombe;
postgres=# \q
# Install rabbitmq
$ rabbitmqctl add_vhost colombe
$ rabbitmqctl add_user colombe password;
$ rabbitmqctl set_permissions -p colombe colombe ".*" ".*" ".*"
# Install nginx
$ cat /etc/nginx/sites-available/colombe
upstream app_server {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80 deferred;
    client_max_body_size 4G;

    server_name colombe.toxi.nu;

    keepalive_timeout 5;

    location / {
        # checks for static file, if not found proxy to app
        try_files $uri @proxy_to_app;
    }

    location /static/ {
        autoindex on;
        alias /srv/colombe/assets/;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://app_server;
    }

    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root /path/to/app/current/public;
    }
}
$ ln -s /etc/nginx/sites-available/colombe /etc/nginx/sites-enabled/colombe
$ systemctl restart nginx
$ cat /etc/systemd/system/colombe-web.service
[Unit]
Description = Colombe
After = network.target

[Service]
User = colombe
Group = colombe
Environment=DJANGO_SETTINGS_MODULE=settings.production
WorkingDirectory = /srv/colombe
ExecStart = /srv/colombe/.venv/bin/waitress-serve --port 8000 --host 127.0.0.1 colombe.wsgi:application

[Install]
WantedBy = multi-user.target
$ cat /etc/systemd/system/colombe-worker.service
[Unit]
Description = Colombe worker
After = network.target

[Service]
User = colombe
Group = colombe
Environment=DJANGO_SETTINGS_MODULE=settings.production
WorkingDirectory = /srv/colombe
ExecStart = /srv/colombe/.venv/bin/colombe run worker

[Install]
WantedBy = multi-user.target
# Configure colombe
$ cd /srv/colombe
$ mkdir settings
$ touch settings/__init__.py
$ cat settings/production.py
from colombe.settings.base import *  # noqa

DEBUG = False
INSTALLED_APPS += ('django_extensions', )

TWITTER_CONSUMER_KEY = 'your-key'
TWITTER_CONSUMER_SECRET = 'your-sercret'

SOCIAL_AUTH_TWITTER_KEY = TWITTER_CONSUMER_KEY
SOCIAL_AUTH_TWITTER_SECRET = TWITTER_CONSUMER_SECRET

INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS = ['colombe.toxi.nu']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'colombe',
        'USER': 'colombe',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = 'amqp://colombe:password@localhost:5672/colombe'
# Install colombe
$ cd /srv/colombe
$ source .venv/bin/activate
(.venv) $ pip install colombe==0.1.0[production]
# Run colombe
$ systemctl enable colombe-web
$ systemctl enable colombe-worker
$ systemctl start colombe-web
$ systemctl start colombe-worker
```