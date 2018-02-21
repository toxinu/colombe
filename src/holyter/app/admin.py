from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from .models import User, BlockList


class BlockListModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'country', 'created_at', 'updated_at', )


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(BlockList, BlockListModelAdmin)
