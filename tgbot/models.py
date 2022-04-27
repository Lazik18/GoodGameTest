from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=150, verbose_name='Имя', null=True)
    telegram_id = models.PositiveIntegerField(verbose_name='Телеграм ID пользователя', unique=True)
    game = models.ForeignKey(to='tgbot.Game', on_delete=models.PROTECT, verbose_name='Основная игра', null=True)
    steam = models.CharField(max_length=150, verbose_name='Имя пользователя в Steam', null=True)
    about = models.TextField(verbose_name='О себе', null=True)
    register_date = models.DateField(verbose_name='Дата регистрации', auto_now_add=True)
    is_register = models.BooleanField(verbose_name='Прошел регистрацию', default=False)
    flag = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'#{self.telegram_id} {self.name}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Game(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'

