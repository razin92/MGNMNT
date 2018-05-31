from django.test import TestCase
import requests

# Create your tests here.
class BotTest(TestCase):

    def send_message(self):
        url = 'http://127.0.0.1/api/notifier/'
        requests.post(url, 'test')

