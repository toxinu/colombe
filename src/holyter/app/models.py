from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django_countries.fields import CountryField


class User(AbstractUser):
    pass


class BlockList(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(max_length=2048, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    users = ArrayField(models.IntegerField(), null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta(object):
        ordering = ['-updated_at', 'name']

    def __str__(self):
        return self.name
