# Generated by Django 4.0.4 on 2022-04-27 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_remove_profile_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='flag',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_register',
            field=models.BooleanField(default=False, verbose_name='Прошел регистрацию'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='about',
            field=models.TextField(null=True, verbose_name='О себе'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='tgbot.game', verbose_name='Основная игра'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='name',
            field=models.CharField(max_length=150, null=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='register_date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата регистрации'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='steam',
            field=models.CharField(max_length=150, null=True, verbose_name='Имя пользователя в Steam'),
        ),
    ]
