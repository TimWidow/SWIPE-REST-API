import pyotp
from django.db.models.signals import pre_save
from django.dispatch import receiver

from api.models import User


def generate_key():
    """ User otp key generator """
    key = pyotp.random_base32()
    if is_unique(key):
        return key
    generate_key()


def is_unique(key):
    try:
        User.objects.get(key=key)
    except User.DoesNotExist:
        return True
    return False


@receiver(pre_save, sender=User)
def create_key(instance, **kwargs):
    """This creates the key for users that don't have keys"""
#    if not instance.key:
#       instance.key = generate_key()
