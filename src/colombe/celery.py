import os

import celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colombe.settings')


class Celery(celery.Celery):
    def on_configure(self):
        pass


app = Celery('colombe', include=['colombe.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')
