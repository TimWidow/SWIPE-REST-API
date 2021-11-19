# coding: utf-8
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import requests
import json

from home import Home
from ws import WSRequests
from twilio.rest import Client
from authy.api import AuthyApiClient

from kivy.network.urlrequest import UrlRequest

# req = UrlRequest()

# client = Client('<your Twilio Account SID here>', '<your Twilio Auth Token here>')
# verify = client.verify.services('<your Twilio Verify Service SID here>')
# verify.verifications.create(to='<your phone number here>', channel='sms')


class Login(BoxLayout):
    ws_url = 'http://127.0.0.1:8000/api/login/'

    def do_login(self, email, password):
        headers = {'content-type': 'application/json'}
        params = {
            'email': email,
            'password': password
        }
        response = requests.post(url=self.ws_url, data=json.dumps(params), headers=headers)
        print(response.text)
        if response.status_code == 200:
            token_dict = json.loads(response.text)
            self.save_token(str=token_dict['token'])
            ws_req = WSRequests()
            user_response = ws_req.get_ws_data(
                action_url='http://127.0.0.1:8000/api/login/',
                params={'username': login}
            )
            if user_response.resp_status == 403:
                print('Доступ запрещён')
            else:
                app = App.get_running_app()
                app.root_window.remove_widget(app.root)
                home_window = Home(username=login, login_window=self)
                app.root_window.add_widget(home_window)
        else:
            print(f'Неправильное имя пользователя или пароль')

    def save_token(self, str):
        with open('token', 'w') as outfile:
            outfile.write(str)
