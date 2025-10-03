from django.contrib import admin
from .models import Word, Game, Guess

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'started_at', 'finished', 'win', 'guesses_used')

@admin.register(Guess)
class GuessAdmin(admin.ModelAdmin):
    list_display = ('game', 'text', 'attempted_at')
