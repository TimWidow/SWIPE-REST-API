# coding: utf-8

# ######################### #
#                           #
# Autor: Jorge Dominguez    #
#                           #
# MandarinaSoft - 2018      #
#                           #
# ######################### #

import requests
import json
import os
import urllib
from kivy.network.urlrequest import UrlRequest


class WSRequests:

    def __init__(self):
        self.url_base = 'http://localhost:8000/'
        self.token = self.load_token()

    def get_ws_data(self, action_url=None, params=None):
        if action_url is None or params is None:
            raise ValueError('URL-адрес или параметры не могут быть пустыми')
        # params = urllib.urlencode(params)
        headers = {
            'Authorization': f'Token {self.token}'
            # 'Content-type': 'application/json',
        }
        req = UrlRequest(
            url=f'{self.url_base}{action_url}',
            req_body=json.dumps(params),
            req_headers=headers,
        )
        req.wait()
        return req

    def load_token(self):
        return self.read_file_contents(path='token')

    @staticmethod
    def read_file_contents(path):
        if os.path.exists(path):
            with open(path) as infile:
                return infile.read().strip()


