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
            inline_keyboard=[[InlineKeyboardButton(text='⚙️ Изменить профиль ⚙️', callback_data='EditProfile')],
                             [InlineKeyboardButton(text='🔎 Искать людей 🔍', callback_data='SearchStart')]])
        bot.sendPhoto(chat_id=user.telegram_id, photo='https://cdn.dribbble.com/users/869811/screenshots/4043532/tinder_dribbble.png',
                      caption='🎲 Меню Тиндер 🎮\n Здесь вы сможете найти людей для совместных игр', reply_markup=keyboard)
    else:
        if update.message.from_user.username is None:
            bot.sendMessage(chat_id=user.telegram_id, text='Пожалуйста, укажите username в вашем профиле телеграм '
                                                           'и попробуйте снова /start 😞')
            return
        user.username = update.message.from_user.username
        user.save()
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Создать профиль ➡️', callback_data='CreateProfile')]])
        bot.sendMessage(chat_id=user.telegram_id, text='Сперва Вам нужно создать профиль ☝️', reply_markup=keyboard)


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
            inline_keyboard=[[InlineKeyboardButton(text='⬅️', callback_data='CreateGameLeft'),
                              InlineKeyboardButton(text='Выбрать', callback_data='CreateGameSelect'),
                              InlineKeyboardButton(text='➡️', callback_data='CreateGameRight')]])
        bot.sendMessage(chat_id=telegram_id, text=f'Выберите игру:\n {game.title}', reply_markup=keyboard)
    elif user.steam is None:
        bot.sendMessage(chat_id=telegram_id, text='Укажите ваш никнейм в Steam:')
        user.flag = 'steam'
        user.save()
    elif user.is_register:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Редактировать профиль', callback_data='EditProfile'),
                              InlineKeyboardButton(text='В меню 🏢', callback_data='BackMenu')]])
        bot.sendMessage(chat_id=telegram_id, text='Изменения сохранены ☑️️', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Редактировать профиль', callback_data='EditProfile'),
                              InlineKeyboardButton(text='В меню 🏢', callback_data='BackMenu')]])
        bot.sendMessage(chat_id=telegram_id, text='Вы успешно зарегистрированы ☑️', reply_markup=keyboard)
        user.is_register = True
        user.vision = True
        user.save()


def edit_profile(telegram_id):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    user = Profile.objects.get(telegram_id=telegram_id)

    if user.vision:
        str_vision = 'виден'
    else:
        str_vision = 'скрыт'
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='⚙️ Имя ⚙️', callback_data='EditName')],
                         [InlineKeyboardButton(text='⚙️ О себе ⚙️', callback_data='EditAbout')],
                         [InlineKeyboardButton(text='⚙️ Основную игру ⚙️', callback_data='EditGame')],
                         [InlineKeyboardButton(text='⚙️ Никнейм Steam ⚙️', callback_data='EditSteam')],
                         [InlineKeyboardButton(text='⚙️ Переключить видимость ⚙️', callback_data='EditVision')],
                         [InlineKeyboardButton(text='🏢 Вернуться в меню 🏢', callback_data='BackMenu')]])
    bot.sendMessage(chat_id=telegram_id, text=f'Что бы вы хотели изменить?\n'
                                              f'Ваш профиль {str_vision}\n'
                                              f'Имя: {user.name}\n'
                                              f'О себе:\n'
                                              f'{user.about}\n'
                                              f'Игра: {user.game}\n'
                                              f'Никнейм в Steam: {user.steam}', reply_markup=keyboard)


def search_select_game(telegram_id, game=Game.objects.first()):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    user = Profile.objects.get(telegram_id=telegram_id)
    user.flag = f'{game.pk}'
    user.save()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='⬅️', callback_data='SearchGameLeft'),
                          InlineKeyboardButton(text='Выбрать', callback_data='SearchGameSelect'),
                          InlineKeyboardButton(text='➡️', callback_data='SearchGameRight')]])
    bot.sendMessage(chat_id=telegram_id, text=f'🔍Выберите игру для поиска людей:\n {game.title}', reply_markup=keyboard)


def search(telegram_id, next_user=None):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)

    if next_user is None:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='В меню 🏢', callback_data='BackMenu'),
                              InlineKeyboardButton(text='Выбрать другую игру', callback_data='SearchStart')]])
        bot.sendMessage(chat_id=telegram_id, text='Пользователей не найдено 😞', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Отправить мои данные ✉️', callback_data=f'SearchSend '
                                                                                              f'{next_user.telegram_id}'),
                              InlineKeyboardButton(text='Следующий ➡️', callback_data=f'SearchNext {next_user.pk}')],
                             [InlineKeyboardButton(text='В меню 🏢', callback_data='BackMenu')]])
        bot.sendMessage(chat_id=telegram_id, text=f'{next_user.name}\n'
                                                  f'Основная игра: {next_user.game}\n'
                                                  f'О себе:\n {next_user.about}\n'
                                                  f'Мой Steam: {next_user.steam}\n'
                                                  f'Зарегистрирован с {next_user.register_date}',
                        reply_markup=keyboard)


def send_profile(telegram_id, for_user):
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)
    user = Profile.objects.get(telegram_id=telegram_id)

    bot.sendMessage(chat_id=for_user, text=f'Пользователю @{user.username} понравилась ваша карточка по игре.🤔\n'
                                           f'Вот его анкета:\n'
                                           f'Имя: {user.name}\n'
                                           f'Основная игра: {user.game}\n'
                                           f'О себе:\n {user.about}\n'
                                           f'Steam: {user.steam}\n'
                                           f'Напишите ему!')


def case_messages(update: Update, context: CallbackContext):
    query = update.callback_query
    current_message = (query.message.chat_id, query.message.message_id)
    user = Profile.objects.get(telegram_id=query.message.chat_id)
    telegram_token = settings.TOKEN
    bot = telepot.Bot(telegram_token)

    if 'SearchStart' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            search_select_game(user.telegram_id)
    elif 'SearchNext' in query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.get(pk=int(user.flag))
            data = query.data.split()
            next_user = Profile.objects.filter(game__id=game.id, pk__gt=int(data[1])) \
                .exclude(pk=user.pk).filter(vision=True).first()
            if next_user is None:
                next_user = Profile.objects.filter(game__id=game.id, pk__gt=int(data[1])) \
                    .exclude(pk=user.pk).filter(vision=True).first()
            search(query.message.chat_id, next_user=next_user)
    elif 'SearchSend' in query.data:
        data = query.data.split()
        send_profile(query.message.chat_id, int(data[1]))
        bot.sendMessage(chat_id=query.message.chat_id, text='Ваш запрос отправлен ✅')
        return
    elif 'EditProfile' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            edit_profile(user.telegram_id)
    elif 'EditVision' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.vision = not user.vision
            user.save()
            create_profile(user.telegram_id)
    elif 'EditName' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.name = None
            user.save()
            create_profile(user.telegram_id)
    elif 'EditAbout' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.about = None
            user.save()
            create_profile(user.telegram_id)
    elif 'EditGame' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.game = None
            user.save()
            create_profile(user.telegram_id)
    elif 'EditSteam' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.steam = None
            user.save()
            create_profile(user.telegram_id)
    elif 'BackMenu' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            command_messages(update, context)
    elif 'CreateProfile' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            create_profile(query.message.chat_id)
    elif 'CreateGameLeft' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__lt=int(user.flag)).last()
            if game is None:
                game = Game.objects.last()
            create_profile(query.message.chat_id, game=game)
    elif 'SearchGameLeft' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__lt=int(user.flag)).last()
            if game is None:
                game = Game.objects.last()
            search_select_game(query.message.chat_id, game=game)
    elif 'CreateGameSelect' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            user.game = Game.objects.get(pk=int(user.flag))
            user.save()
            create_profile(query.message.chat_id)
    elif 'SearchGameSelect' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.get(pk=int(user.flag))
            next_user = Profile.objects.filter(game__id=game.id, pk__gt=user.pk).first()
            if next_user is None:
                next_user = Profile.objects.filter(game__id=game.id, pk__lt=user.pk).first()
            search(query.message.chat_id, next_user=next_user)
    elif 'CreateGameRight' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__gt=int(user.flag)).first()
            if game is None:
                game = Game.objects.first()
            create_profile(query.message.chat_id, game=game)
    elif 'SearchGameRight' == query.data:
        try:
            bot.deleteMessage(current_message)
        except telepot.exception.TelegramError:
            pass
        finally:
            game = Game.objects.filter(pk__gt=int(user.flag)).first()
            if game is None:
                game = Game.objects.first()
            search_select_game(query.message.chat_id, game=game)


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
