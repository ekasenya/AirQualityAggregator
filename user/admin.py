from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = UserAdmin.list_display + ('avatar',)
