from django.shortcuts import redirect

from . import models



class EmailAuthBackend(object):

    @staticmethod
    def authenticate(email=None, password=None):
        try:
            user = models.User.objects.get(email=email)
        except Exception:
            return None

        if not user.check_password(password):
            return None

        return user

    @staticmethod
    def get_user(user_id):
        try:
            return models.User.objects.get(pk=user_id)
        except Exception:
            return None


class PhoneAuthBackend(object):

    @staticmethod
    def authenticate(phone=None, password=None):
        try:
            user = models.User.objects.get(related_phone__Mobile=phone)
            phone_number = models.PhoneModel.objects.get(user_id=user.id)
            if phone_number.isVerified:
                pass
            else:
                redirect('phone-login', phone=phone_number.Mobile)
        except Exception:
            return None

        if not user.check_password(password):
            return None

        return user

    @staticmethod
    def get_user(user_id):
        try:
            return models.User.objects.get(pk=user_id)
        except Exception:
            return None