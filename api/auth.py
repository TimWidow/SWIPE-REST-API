from django.shortcuts import redirect
from .models import User
from .verify import send, check


class EmailAuthBackend(object):

    @staticmethod
    def authenticate(email=None, password=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        return user

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class PhoneAuthBackend(object):

    @staticmethod
    def authenticate(phone=None):
        try:
            user = User.objects.get(phone=phone)

        except User.DoesNotExist:
            return redirect('registration')

        return user

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
