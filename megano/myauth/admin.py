from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, Avatar


class AvatarInline(admin.StackedInline):
    model = Avatar


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'fullName', 'email', 'phone',)
    list_display_links = ('pk', 'fullName',)
    inlines = [AvatarInline]
