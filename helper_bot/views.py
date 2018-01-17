from django.shortcuts import render
from .models import Language, SystemMessage, TGUser, Menu, MenuItem, MenuGroup, FAQ, TvSettings, TvModel, New
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from telepot.loop import MessageLoop
from .decorator import check_msg
from .emodji import converter
from django.utils import timezone
from .token import TOKEN
from django.contrib.auth.decorators import login_required
import telepot
import time

#КОСТЫЛЬ
def deimojize(text):
    if text == '🇷🇺 Русский':
        return 'RUS'
    elif text == '🇺🇿 Uzbekcha':
        return 'UZB'

#Глобальные переменные
bot = telepot.Bot(TOKEN)

def global_strings(msg):
    global content_type, chat_type, chat_id, user_id, lang, text, tguser
    content_type, chat_type, chat_id = telepot.glance(msg)
    user_id = msg['from']['id']
    text = msg['text']
    tguser = user_checking(msg)
    lang = ('RUS')
    if tguser.language != None:
        lang = tguser.language.code

#Запись данных о пользователе
def user_checking(msg):
    source = msg['from']
    lng = Language.objects.get_or_create(name='Русский', code='RUS', ico=':rus:')[0]
    username, first_name, last_name = 'None', 'None', 'None'
    if 'first_name' in source:
        first_name = source['first_name']
    if 'last_name' in source:
        last_name = source['last_name']
    if 'username' in source:
        username = source['username']
    user_id = msg['from']['id']
    tg_user = TGUser.objects.filter(tg_id=user_id)
    if len(tg_user) == 0:
        new_user = TGUser.objects.create(
            tg_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            date_registration=timezone.now().date(),
            last_seen=timezone.now(),
            language=lng,
        )
        print(new_user.id, 'создан')
        return new_user
    elif len(tg_user) > 1:
        print('Найдено %s пользователей' % len(tg_user))
        return None
    print(tg_user[0])
    return tg_user[0]

#Проверка на наличие языка в системе
def CheckLang(msg):
    lng = Language.objects.all()
    lang_list = ['%s %s' % (converter(language.ico), language.name) for language in lng]
    if msg in lang_list:
        return msg


def GetMenu(menu_item):
    try:
        menu = Menu.objects.get(menu_item__menu_item=menu_item, language__code=lang, enabled=True)
        return menu
    except:
        error = 'Пункт меню %s(%s) не найден' % (menu_item, lang)
        bot.sendMessage(chat_id, error)

def GetSystemMessage(menu_item, msg_type):
    try:
        message = SystemMessage.objects.get(menu_item__menu_item=menu_item, type_of_message=msg_type, language__code=lang)
        return message
    except:
        error = 'Сообщение %s%s(%s) не найдено' % (menu_item, msg_type, lang)
        bot.sendMessage(chat_id, error)

#Кнопки управления
class Keyboard():
    def menu_extractor(**kwargs):
        menu_group = kwargs.pop('group', 'main_menu')
        menu = Menu.objects.filter(menu_group__group=menu_group, language__code=lang, enabled=True).order_by('sequence_number')
        return menu

    def keyboard_template(**kwargs):
        group = kwargs.pop('group', 'main_menu')
        menu_set = Keyboard.menu_extractor(group=group)
        keys = {menu.name: [KeyboardButton(text='%s %s' % (converter(menu.ico), menu.name))]
                for menu in menu_set
                }
        keyboard = ReplyKeyboardMarkup(
            keyboard=[keys[x.name] for x in menu_set],
            resize_keyboard=True,
            one_time_keyboard=False,
        )
        return keyboard

    def inline_keyboard(**kwargs):
        pass

    def language_keys(*args):
        lang_set = Language.objects.filter(enabled=True)
        keys = {menu.code: [KeyboardButton(text='%s %s' % (converter(menu.ico), menu.name))]
                for menu in lang_set
                }
        keyboard = ReplyKeyboardMarkup(
            keyboard=[keys[x.code] for x in lang_set],
            resize_keyboard=True,
            one_time_keyboard=False,
        )
        return keyboard

    def tv_settings_keyboard(**kwargs):
        back_to_main = Menu.objects.get(menu_item__menu_item='main_menu', language__code=lang, enabled=True)
        base_object = kwargs.pop('object')
        main = [KeyboardButton(text='%s %s' % (converter(back_to_main.ico), back_to_main.name))]
        if base_object == FAQ:
            faq_menu = {element.question: [KeyboardButton(text='%s %s' % (converter(element.ico), element.question))]
                        for element in base_object.objects.filter(language__code=lang).order_by('position_number')
                        }
            keys = [faq_menu[x.question] for x in base_object.objects.filter(language__code=lang).order_by('position_number')]
        else:
            tv_models = {model.vendor: [KeyboardButton(text='%s %s' % (converter(model.ico), model.vendor))]
                         for model in base_object.objects.all(language__code=lang).order_by('position_number')
                         }
            keys = [tv_models[x.vendor] for x in base_object.objects.filter(language__code=lang).order_by('position_number')]
        keys.append(main)
        keyboard = ReplyKeyboardMarkup(
            keyboard=keys,
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        return keyboard

    def news_keyboard(**kwargs):
        back_to_main = Menu.objects.get(menu_item__menu_item='main_menu', language__code=lang, enabled=True)
        main = [KeyboardButton(text='%s %s' % (converter(back_to_main.ico), back_to_main.name))]
        keys = [['1️⃣ Последняя новость'], ['5️⃣ Последних новостей'], ['1️⃣0️⃣ Последних новостей'], main]
        keyboard = ReplyKeyboardMarkup(
            keyboard=keys,
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        return keyboard


#Блок меню
class MenuSet():
    def menu_template(**kwargs):
        menu_group = kwargs.pop('menu_group')
        message_type = kwargs.pop('msg_type')
        menu_item = kwargs.pop('menu_item', 'main_menu')
        keys = Keyboard.keyboard_template(group=menu_group)
        message = GetSystemMessage(menu_item, message_type).text
        bot.sendMessage(chat_id, message, reply_markup=keys)

    def select_language_menu(**kwargs):
        message_type = kwargs.pop('msg_type')
        keys = Keyboard.language_keys()
        message = GetSystemMessage('language', message_type).text
        bot.sendMessage(chat_id, message, reply_markup=keys)

    def base_menu(**kwargs):
        message_type = kwargs.pop('msg_type', '_description')
        object = kwargs.pop('object')
        keys = Keyboard.tv_settings_keyboard(object=object)
        message = GetSystemMessage('setup_tv', message_type).text
        if object == FAQ:
            message = GetSystemMessage('FAQ', message_type).text
        bot.sendMessage(chat_id, message, reply_markup=keys)

    def tv_settings_menu(**kwargs):
        model = kwargs.pop('model')
        settings = TvSettings.objects.filter(language__code=lang, model__vendor=model).order_by('sequence_number')
        for each in settings:
            text = 'Шаг номер %s \n%s' % (each.sequence_number, each.text)
            bot.sendPhoto(chat_id, each.image, text)

    def faq_menu(**kwargs):
        question = kwargs.pop('question')
        question = FAQ.objects.get(language__code=lang, question__icontains=question)
        bot.sendMessage(chat_id, '%s \n \n%s' % (question.question, question.answer))

    def news(**kwargs):
        message_type = kwargs.pop('msg_type', '_description')
        keys = Keyboard.news_keyboard()
        message = GetSystemMessage('news', message_type).text
        bot.sendMessage(chat_id, message, reply_markup=keys)

    def get_news(**kwargs):
        value = kwargs.pop('value', 1)
        news = New.objects.filter(language__code=lang, enabled=True).order_by('-date_pub')[:value]
        for each in news:
            picture = each.image
            title = each.name
            date = each.date_pub
            news_text = each.text
            text = '%s - %s \n%s' % (date, title, news_text)
            if picture is None:
                bot.sendMessage(chat_id, text)
            else:
                bot.sendPhoto(chat_id, picture, text)

#Тело бота
@check_msg
def bot_body(msg):
    print(msg)
    menu = Menu.objects.filter(language__code=lang, enabled=True)
    menu_set = {'items': {'%s %s' % (converter(x.ico), x.name): x.menu_item.menu_item for x in menu}, }
    menu_extract = None
    if text in menu_set['items']:
        menu_extract = menu_set['items'][text]
    tv_models = {'%s %s' % (converter(tv.ico), tv.vendor): tv.vendor for tv in TvModel.objects.all()}
    faq = {'%s %s' % (converter(element.ico), element.question): element.question for element in FAQ.objects.all()}
    news = {'1️⃣ Последняя новость': 1, '5️⃣ Последних новостей': 2, '1️⃣0️⃣ Последних новостей': 3}
    if text == '/start':
        bot.sendMessage(chat_id, 'Успех')
        MenuSet.menu_template(menu_group='main_menu', msg_type='_description')
    elif text == CheckLang(text):
        tguser.language = Language.objects.get(code=deimojize(text))
        tguser.save()
        global_strings(msg)
        MenuSet.menu_template(menu_group='main_menu', msg_type='_description')
    elif text in menu_set['items']:
        if menu_extract == 'language':
            MenuSet.select_language_menu(msg_type='_description')
        elif menu_extract == 'setup_tv':
            MenuSet.base_menu(object=TvModel)
        elif menu_extract == 'FAQ':
            MenuSet.base_menu(object=FAQ)
        elif menu_extract == 'news':
            MenuSet.news()
        else:
            MenuSet.menu_template(menu_item=menu_extract, menu_group=menu_extract, msg_type='_description')
    elif text in tv_models:
        MenuSet.tv_settings_menu(model=tv_models[text])
    elif text in faq:
        MenuSet.faq_menu(question=faq[text])
    elif text in news:
        MenuSet.get_news(value=news[text])

#Проверка чата на приватность
def personal_bot(msg):
    global_strings(msg)
    if chat_type == 'private' and tguser.language == None and text == '/start':
        bot.sendMessage(chat_id, 'Привет!')
        MenuSet.select_language_menu(msg_type='_description')
    elif chat_type == 'private':
        bot_body(msg)
    else:
        message = 'Я не буду с Вами разговаривать при всех, только с глазу на глаз.'
        bot.sendMessage(chat_id, message)

#Запуск бота
@login_required()
def run_bot(request):
    MessageLoop(bot, {'chat': personal_bot, } ).run_as_thread()
    print('Слушаю...')

    while 1:
       time.sleep(3)


#Быстрое создание базовых объектов для работы бота
@login_required()
def fast_start(request):
    lng = Language.objects.get_or_create(name='Русский', code='RUS', ico=':rus:')[0]
    for element in MenuGroup.menu_group:
        MenuGroup.objects.get_or_create(group=element[0])
    for element in MenuItem.menu_item_list:
        MenuItem.objects.get_or_create(menu_item=element[0])
    for menu_item in MenuItem.objects.all():
        Menu.objects.get_or_create(language=lng, ico=':def:', menu_item=menu_item, name=menu_item.menu_item)
    for element in MenuItem.objects.all():
        for each in SystemMessage.type_list:
            SystemMessage.objects.get_or_create(menu_item=element, type_of_message=each[0], text='%s%s' % (element.menu_item, each[0]), language=lng)

    return render(request, 'index.html')