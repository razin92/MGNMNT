from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from telepot.loop import MessageLoop
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from .models import AuthorizedUser
from .token import pst_notifier_bot as TOKEN
from .token import test_messaging_bot as TEST_TOKEN
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from basicauth.decorators import basic_auth_required
from django.views.decorators.csrf import csrf_exempt
import codecs
import telepot
import json
import time

bot = telepot.Bot(TOKEN)

#Словарь из входящего Json
def json_extractor(msg):
    return dict(msg)

#Часто используемые данные
def base_data(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    data = {'content_type': content_type, 'chat_type': chat_type, 'chat_id': chat_id}
    return data

class Keyboard():
    def registration_key(self):
        key1 = [KeyboardButton(text='🤝 Регистрация', request_contact=True)]
        keyboard = ReplyKeyboardMarkup(
                keyboard=[key1, ],
                resize_keyboard=True,
                one_time_keyboard=True,
                selective=True,
            )
        return keyboard


#Проверка на наличие полей входящего контакта
def user_data_check(msg, user_data):
    if user_data in json_extractor(msg)['contact']:
        return json_extractor(msg)['contact'][user_data]

def user_creator(msg):
    try:
        if 'username' in json_extractor(msg)['from']:
            username = json_extractor(msg)['from']['username']
        else:
            username = None
        user_id = user_data_check(msg, 'user_id')
        telephone = user_data_check(msg, 'phone_number')
        first_name = user_data_check(msg, 'first_name')
        last_name = user_data_check(msg, 'last_name')
        user = AuthorizedUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            user_name=username,
            user_id=user_id,
            telephone=telephone
        )
        message = '🤝 Регистрация успешно завершена'
        return (message, user)
    except:
        message = '🤝 Вы уже зарегистрированы'
        return (message, None)

#Проверка на правльность принятного контакта для регистрации
def registration_control(msg):
    contact = json_extractor(msg)['contact']['user_id']
    sender = json_extractor(msg)['from']['id']
    return contact == sender

def registration(msg):
    content_type = base_data(msg)['content_type']
    chat_id = base_data(msg)['chat_id']
    if content_type == 'contact':
        if registration_control(msg):
            message, user = user_creator(msg)
            bot.sendMessage(chat_id, message)
            return (True, user)
        else:
            user = AuthorizedUser.objects.filter(user_id=chat_id)
            if user:
                message = '🤝 Вы уже зарегистрированы'
                bot.sendMessage(chat_id, message)
                return (None, None)
            else:
                message = 'Нельзя использовать чужие контакты для регистрации! Поделитесь своим контактом. Попробуем еще раз...'
                bot.sendMessage(chat_id, message)
                return (None, None)

def authorization(msg):
    chat_id = base_data(msg)['chat_id']
    user_id = json_extractor(msg)['from']['id']
    registration(msg)
    user = [x for x in AuthorizedUser.objects.filter(user_id=user_id).all()]

    if user:
        return (True, user[0])

    else:
        keys = Keyboard.registration_key(msg)
        message = 'Привет, незнакомец. Чтобы начать использовать бота, необходимо пройти регистрацию'
        bot.sendMessage(chat_id, message, reply_markup=keys)
        return (False, None)

def authentication(msg):
    chat_id = base_data(msg)['chat_id']


    if authorization(msg)[0]:
        user = authorization(msg)[1]
        phone = user.telephone
        staff = [x for x in AuthorizedUser.objects.filter(telephone=phone, authorized=True).all()]

        if staff:
            return (True, staff[0])

        else:
            message = "У Вас недостаточно прав чтобы продолжить работу с ботом. Обратитесь к администратору"
            bot.sendMessage(chat_id, message)
            return (False, None)

def bot_body(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print(dict(msg))
    if authorization(msg)[0]:
        if content_type == 'text' and msg['text'] == '/start':
            bot.sendMessage(chat_id, 'Вы в системе')
            if authentication(msg)[0]:
                bot.sendMessage(chat_id,'Все готово!')

def personal_bot(msg):
    chat_type = base_data(msg)['chat_type']
    chat_id = base_data(msg)['chat_id']
    if chat_type == 'private':
        bot_body(msg)
    else:
        message = 'Я не буду с Вами разговаривать при всех, только с глазу на глаз.'
        bot.sendMessage(chat_id, message)

@login_required()
def run_bot(request):
    MessageLoop(bot, {'chat': personal_bot} ).run_as_thread()
    print('Слушаю...')

    while 1:
        time.sleep(10)

@method_decorator(basic_auth_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class Message(View):

    def get(self, request):

        response = {
            'result': 'get_ok',
            'your_ip': '%s' % request.META['REMOTE_ADDR'],
        }
        #return render(request, template_name='api/test.html', context={'response': response})
        return JsonResponse(response)

    def post(self, request):
        users = AuthorizedUser.objects.filter(authorized=True, user_id__isnull=False)
        body = request.body.decode('utf-8', 'ignore')
        try:
            result = json.loads(body)
        except:
            result = body
        text = 'Ip_add: %s \n' \
               'Post: %s \n' % \
               (request.META['REMOTE_ADDR'],
                result)

        for each in users:
            bot.sendMessage(each.user_id, text)

        response = {
            'result': 'post_ok'
        }

        return JsonResponse(response)


@method_decorator(basic_auth_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class MessageTest(View):

    def get(self, request):

        response = {
            'result': 'get_ok',
            'yours_ip': '%s' % request.META['REMOTE_ADDR'],
        }
        return JsonResponse(response)

    def post(self, request):
        users = ['50786101', '119920517']
        test_bot = telepot.Bot(TEST_TOKEN)
        body = request.body.decode('utf-8', 'ignore')
        try:
            result = json.loads(body)
        except:
            result = body
        text = 'Ip_add: %s \n' \
               'Post: %s \n' % \
               (request.META['REMOTE_ADDR'],
                result)

        for each in users:
            test_bot.sendMessage(each, text)

        response = {
            'result': 'post_ok'
        }

        return JsonResponse(response)