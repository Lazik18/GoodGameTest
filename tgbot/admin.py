from django.contrib import admin

from .models import Profile, Game


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game', 'steam')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
