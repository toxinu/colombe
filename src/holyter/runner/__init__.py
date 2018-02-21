import os

import click
from django.utils.module_loading import import_string

import holyter


@click.group()
@click.option(
    '--settings',
    default='',
    envvar='DJANGO_SETTINGS_MODULE',
    help='Path to settings module.',
    metavar='PATH')
@click.version_option(version=holyter.__version__)
@click.pass_context
def cli(ctx, settings):
    """Holyter is an emailing platform.

    Default settings module is `holyter.settings` but
    it can be overridden with `DJANGO_CONFIG_MODULE`
    or with `--settings` parameter.
    """
    # Elevate --settings option to DJANGO_CONFIG_MODULE env var
    if settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holyter.settings')


list(
    map(lambda cmd: cli.add_command(import_string(cmd)),
        ('holyter.runner.commands.help.help',
         'holyter.runner.commands.django.django', )))


def make_django_command(name, django_command=None, help=None):
    "A wrapper to convert a Django subcommand a Click command"
    if django_command is None:
        django_command = name

    @click.command(
        name=name,
        help=help,
        add_help_option=False,
        context_settings=dict(
            ignore_unknown_options=True, ))
    @click.argument('management_args', nargs=-1, type=click.UNPROCESSED)
    @click.pass_context
    def inner(ctx, management_args):
        from holyter.runner.commands.django import django
        ctx.params['management_args'] = (django_command, ) + management_args
        ctx.forward(django)

    return inner


def main():
    cli(obj={}, max_content_width=100)
