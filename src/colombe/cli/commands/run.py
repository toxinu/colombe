import sys
import logging
from multiprocessing import cpu_count

import click

log = logging.getLogger('munch.apps.transactional')


@click.group()
def run():
    "Run a service."


@run.command()
@click.option('--pool', '-P', help=(
    'Pool implementation: prefork (default), '
    'eventlet, gevent, solo or threads.'), default='prefork')
@click.option('--hostname', '-n', help=(
    'Set custom hostname, e.g. \'w1.%h\'. Expands: %h'
    '(hostname), %n (name) and %d, (domain).'))
@click.option('--concurrency', '-c', default=cpu_count(), help=(
    'Number of child processes or threads to spawn. The '
    'default is the number of CPUs available on your system.'))
@click.option('--quiet', '-q', is_flag=True, default=False)
@click.option('--no-color', is_flag=True, default=False)
@click.option(
    '--autoreload', is_flag=True,
    default=False, help='Enable autoreloading.')
@click.option(
    '--loglevel', '-l', help='Logging level',
    type=click.Choice(
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL']))
def worker(**options):
    "Run background worker instance."
    from django.conf import settings
    if hasattr(settings, 'CELERY_ALWAYS_EAGER') and settings.CELERY_ALWAYS_EAGER:
        raise click.ClickException(
            'Disable CELERY_ALWAYS_EAGER in your settings file to spawn workers.')

    from colombe.celery import app
    pool_cls = options.pop('pool')
    worker = app.Worker(pool_cls=pool_cls, **options)
    worker.start()
    sys.exit(worker.exitcode)
