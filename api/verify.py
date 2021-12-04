from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

client = Client('AC480fdde57f3414684e58bdd13318d15a', '6ee15750966fa4e4cde998bed1855a36')
verify = client.verify.services('VA862953786dba5d5dd8398d14e6f0de31')


def send(phone):
    verify.verifications.create(to=phone, channel='sms')


def check(phone, code):
    try:
        result = verify.verification_checks.create(to=phone, code=code)
        print(result.status)
    except TwilioRestException as error:
        print(error)
        return False
    return result.status == 'approved'


print(check('+380662863099', '4804'))
