from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator

class Word(models.Model):
    text = models.CharField(max_length=5, unique=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)
    win = models.BooleanField(default=False)
    guesses_allowed = models.PositiveSmallIntegerField(default=5)
    guesses_used = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'Game({self.user.username}, {self.word.text}, {self.started_at.date()})'

class Guess(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='guesses')
    text = models.CharField(max_length=5, validators=[
        RegexValidator(regex=r'^[A-Z]{5}$', message='Guess must be 5 uppercase letters.')
    ])
    status = models.JSONField(default=list)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.text} @ {self.attempted_at}'
