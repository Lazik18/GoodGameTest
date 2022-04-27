from django.core.management.base import BaseCommand
from django.conf import settings

from tgbot.models import Profile, Game

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from telegram.utils.request import Request
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackQueryHandler, CallbackContext, Filters


def command_messages(update: Update, context: CallbackContext):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    try:
        chat_id = update.message.chat_id
    except AttributeError:
        chat_id = update.callback_query.message.chat_id

    user, _ = Profile.objects.get_or_create(telegram_id=chat_id)
    if user.is_register:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Изменить профиль', callback_data='EditProfile')],
                             [InlineKeyboardButton(text='Искать людей', callback_data='Search')]])
        bot.sendMessage(chat_id=user.telegram_id, text=' Меню Тиндер', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Создать профиль', callback_data='CreateProfile')]])
        bot.sendMessage(chat_id=user.telegram_id, text='Сперва Вам нужно создать профиль', reply_markup=keyboard)


def messages(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    try:
        user = Profile.objects.get(telegram_id=chat_id)
        if user.flag == 'name':
            user.name = update.message.text
            user.flag = None
            user.save()
            create_profile(chat_id)
        elif user.flag == 'about':
            user.about = update.message.text
            user.flag = None
            user.save()
            create_profile(chat_id)
        elif user.flag == 'steam':
            user.steam = update.message.text
            user.flag = None
            user.save()
            create_profile(chat_id)
    except Profile.DoesNotExist:
        bot.sendMessage(chat_id=chat_id, text='Используйте команду: /start')


def create_profile(telegram_id, game=Game.objects.first()):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    user = Profile.objects.get(telegram_id=telegram_id)

    if user.name is None:
        bot.sendMessage(chat_id=telegram_id, text='Напишите ваше имя:')
        user.flag = 'name'
        user.save()
    elif user.about is None:
        bot.sendMessage(chat_id=telegram_id, text='Напишите небольшой текст о себе:')
        user.flag = 'about'
        user.save()
    elif user.game is None:
        user.flag = f'{game.pk}'
        user.save()
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='<', callback_data='GameLeft'),
                              InlineKeyboardButton(text='Выбрать', callback_data='GameSelect'),
                              InlineKeyboardButton(text='>', callback_data='GameRight')]])
        bot.sendMessage(chat_id=telegram_id, text=f'Выберите игру:\n {game.title}', reply_markup=keyboard)
    elif user.steam is None:
        bot.sendMessage(chat_id=telegram_id, text='Укажите ваш никнейм в Steam:')
        user.flag = 'steam'
        user.save()
    elif user.is_register:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Редактировать профиль', callback_data='EditProfile'),
                              InlineKeyboardButton(text='В меню', callback_data='BackMenu')]])
        bot.sendMessage(chat_id=telegram_id, text='Изменения сохранены', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Редактировать профиль', callback_data='EditProfile'),
                              InlineKeyboardButton(text='В меню', callback_data='BackMenu')]])
        bot.sendMessage(chat_id=telegram_id, text='Вы успешно зарегистрированы', reply_markup=keyboard)
        user.is_register = True
        user.save()


def edit_profile(telegram_id):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    user = Profile.objects.get(telegram_id=telegram_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Имя', callback_data='EditName')],
                         [InlineKeyboardButton(text='О себе', callback_data='EditAbout')],
                         [InlineKeyboardButton(text='Основную игру', callback_data='EditGame')],
                         [InlineKeyboardButton(text='Никнейм Steam', callback_data='EditSteam')],
                         [InlineKeyboardButton(text='Вернуться в меню', callback_data='BackMenu')]])
    bot.sendMessage(chat_id=telegram_id, text=f'Что бы вы хотели изменить?\n'
                                              f'Имя: {user.name}\n'
                                              f'О себе:\n'
                                              f'{user.about}\n'
                                              f'Игра: {user.game}\n'
                                              f'Никнейм в Steam: {user.steam}', reply_markup=keyboard)


def search(telegram_id, game=Game.objects.first()):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    user = Profile.objects.get(telegram_id=telegram_id)
    user.flag = f'{game.pk}'
    user.save()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='<', callback_data='GameLeftSearch'),
                          InlineKeyboardButton(text='Выбрать', callback_data='GameSelectSearch'),
                          InlineKeyboardButton(text='>', callback_data='GameRightSearch')]])
    bot.sendMessage(chat_id=telegram_id, text=f'Выберите игру:\n {game.title}', reply_markup=keyboard)


def case_messages(update: Update, context: CallbackContext):
    query = update.callback_query
    current_message = (query.message.chat_id, query.message.message_id)
    user = Profile.objects.get(telegram_id=query.message.chat_id)
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)

    if 'Search' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            search(user.telegram_id)
    elif 'EditProfile' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            edit_profile(user.telegram_id)
    elif 'EditName' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.name = None
            user.save()
            create_profile(user.telegram_id)
    elif 'EditAbout' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.about = None
            user.save()
            create_profile(user.telegram_id)
    elif 'EditGame' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.game = None
            user.save()
            create_profile(user.telegram_id)
    elif 'EditSteam' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.steam = None
            user.save()
            create_profile(user.telegram_id)
    elif 'BackMenu' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            command_messages(update, context)
    elif 'CreateProfile' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            create_profile(query.message.chat_id)
    elif 'GameLeft' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__lt=int(user.flag)).last()
            if game is None:
                game = Game.objects.last()
            create_profile(query.message.chat_id, game=game)
    elif 'GameLeftSearch' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__lt=int(user.flag)).last()
            if game is None:
                game = Game.objects.last()
            search(query.message.chat_id, game=game)
    elif 'GameSelect' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.game = Game.objects.get(pk=int(user.flag))
            user.save()
            create_profile(query.message.chat_id)
    elif 'GameSelectSearch' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.game = Game.objects.get(pk=int(user.flag))
            user.save()
            search(query.message.chat_id)
    elif 'GameRight' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__gt=int(user.flag)).first()
            if game is None:
                game = Game.objects.first()
            create_profile(query.message.chat_id, game=game)
    elif 'GameRightSearch' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__gt=int(user.flag)).first()
            if game is None:
                game = Game.objects.first()
            search(query.message.chat_id, game=game)


class Command(BaseCommand):
    help = 'Телеграм - бот'

    def handle(self, *args, **options):
        request = Request(connect_timeout=0.5, read_timeout=1.0, con_pool_size=12)
        telegram_token = settings.TOKEN
        bot = Bot(request=request, token=telegram_token)

        updater = Updater(bot=bot)

        cmd_handler = CommandHandler(command='start', callback=command_messages)
        updater.dispatcher.add_handler(cmd_handler)

        buttons_handler = CallbackQueryHandler(callback=case_messages)
        updater.dispatcher.add_handler(buttons_handler)

        msg_handler = MessageHandler(filters=Filters.text, callback=messages)
        updater.dispatcher.add_handler(msg_handler)

        updater.start_polling()
        updater.idle()
