import logging

from .celery import app as celery

log = logging.getLogger(__name__)


@celery.task
def synchronize_subscription(user_id, to_add, to_remove):
    from .models import User

    user = User.objects.get(pk=user_id)

    twitter = user.twitter

    log.info('Adding {} users from "{}" block list...'.format(len(to_add), user))
    for user_id in to_add:
        twitter.create_block(user_id)

    log.info('Removing {} users from "{}" block list...'.format(len(to_remove), user))
    for user_id in to_remove:
        twitter.destroy_block(user_id)
