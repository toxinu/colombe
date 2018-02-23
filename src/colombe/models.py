from django.urls import reverse
from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django_countries.fields import CountryField

from social_django.utils import load_strategy

from .twitter import Twitter
from .tasks import synchronize_subscription


class BaseModelMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__initial_fields = {}
        for field in self._meta.fields:
            if field.name in self.fields_to_watch:
                self.__initial_fields[field.name] = getattr(self, field.name)

    def pre_save(self, *args, **kwargs):
        pass

    def post_save(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        self.pre_save(*args, **kwargs)
        result = super().save(*args, **kwargs)
        self.post_save(*args, **kwargs)
        return result

    def get_initial(self, name):
        return self.__initial_fields.get(name)

    def has_changed(self, name):
        if name not in self.fields_to_watch:
            raise Exception("This field is not watched")
        return getattr(self, name) != self.__initial_fields.get(name)


class User(AbstractUser):
    subscriptions = models.ManyToManyField('BlockList', through='Subscription')

    @property
    def social(self):
        return self.social_auth.get(provider='twitter')

    @property
    def access_token(self):
        return self.social.get_access_token(load_strategy()).get('oauth_token')

    @property
    def access_token_secret(self):
        return self.social.get_access_token(load_strategy()).get('oauth_token_secret')

    @property
    def twitter(self):
        return Twitter(self.access_token, self.access_token_secret)

    def subscribe_to_block_list(self, block_list):
        subscription = Subscription.objects.create(user=self, block_list=block_list)

        synchronize_subscription.delay(self.id, block_list.users, [])

    def unsubscribe_to_block_list(self, block_list):
        Subscription.objects.filter(user=self, block_list=block_list).delete()

        synchronize_subscription.delay(self.id, [], block_list.users)


class BlockList(BaseModelMixin, models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(max_length=2048, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    users = ArrayField(models.BigIntegerField(), null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    fields_to_watch = ['users']

    class Meta:
        ordering = ['-updated_at', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('block-list-detail', kwargs={'pk': self.pk})

    @property
    def users_count(self):
        if self.users:
            return len(self.users)

        return 0

    @cached_property
    def subscribers(self):
        return Subscription.objects.filter(block_list=self).count()

    def post_save(self, *args, **kwargs):
        if self.has_changed('users'):
            self.synchronize_subscriptions()

    def synchronize_subscriptions(self, ids_to_remove=[], ids_to_add=[]):
        initial_users = self.get_initial("users")

        to_add = set(self.users or []).difference(initial_users or [])
        to_remove = set(initial_users or []).difference(self.users or [])

        for subscription in Subscription.objects.filter(
                block_list=self, enabled=True).only('id', 'user').select_related('user'):
            synchronize_subscription.delay(subscription.user.id, to_add, to_remove)


class Subscription(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    block_list = models.ForeignKey('BlockList', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'block_list')
