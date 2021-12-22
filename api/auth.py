from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from .models import User
from .verify import send, check


class EmailAuthBackend(object):

    @staticmethod
    def authenticate(email=None, password=None):
        try:
            user = User.objects.get(email=email)

            if not user.check_password(password):
                return None
            else:
                return user

        except User.DoesNotExist:
            return None

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
            if not user.is_active:
                return 'This user has been deactivated.'
            else:
                return user

        except User.DoesNotExist:
            return redirect('registration')

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
