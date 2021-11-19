from datetime import datetime, timedelta
import jwt
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, ForeignKey, CASCADE, \
    EmailField, ImageField, BooleanField, DateTimeField, CharField, FloatField, \
    FileField, TextField, IntegerField
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from swipe import settings


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    NOTIFY = (
        ('ME', _('Мне')),
        ('MEANDAGENT', _('Мне и агенту')),
        ('AGENT', _('Агенту')),
        ('OFF', _('Отключить'))
    )
    ROLES = (
        ('USER', _('Клиент')),
        ('AGENT', _('Агент')),
        ('NOTARY', _('Нотариус')),
        ('DEPART', _('Отдел продаж')),
        ('SYSTEM', _('Администрация Swipe'))
    )
    phone = PhoneNumberField(_('phone'), unique=True, region='UA')
    verified = BooleanField(default=False)
    email = EmailField(_('email address'), unique=True)
    avatar = ImageField('Аватар', upload_to='images/user/', blank=True, null=True)
    subscribe = BooleanField(default=False)
    subscribe_expired = DateTimeField(blank=True, null=True)
    notification = CharField(max_length=10, choices=NOTIFY, default='ME')
    role = CharField(max_length=8, choices=ROLES, default='USER')
    agent_first_name = CharField(_('agent first name'), max_length=150, blank=True)
    agent_last_name = CharField(_('agent last name'), max_length=150, blank=True)
    agent_email = EmailField(blank=True, null=True)
    agent_phone = PhoneNumberField(region='UA', blank=True, null=True)

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    class Meta:
        app_label = 'api'


class House(Model):
    HOUSE_CURRENT_STATUS = (
        ('Сдан', 'Сдан'),
        ('Не сдан', 'Не сдан')
    )
    HOUSE_STATUS = (
        ('Квартиры', 'Квартиры'),
        ('Офис', 'Офис'),
    )
    BUILDING_TECHNOLOGY = (
        ('Монолитный каркас с керамзитом', 'Монолитный каркас с керамзитом'),
        ('Панельные', 'Панельные')
    )
    HOUSE_TYPE = (
        ('Многоквартирный', 'Многоквартирный'),
        ('Частный', 'Частный')
    )
    HOUSE_TERRITORY_TYPE = (
        ('Закрытая, охраняемая', 'Закрытая, охраняемая'),
        ('Открытая', 'Открытая')
    )
    INVOICE_TYPE = (
        ('Платежи', 'Платежи'),
        ('Автоплатеж', 'Автоплатеж')
    )
    HEATING_TYPE = (
        ('Центральное', 'Центральное'),
        ('Личное', 'Личное')
    )
    WATER_TYPE = (
        ('Канализация', 'Канализация'),
        ('Яма', 'Яма')
    )
    address = CharField(max_length=255)
    house_status = CharField(choices=HOUSE_STATUS, max_length=55)
    building_technologies = CharField(choices=BUILDING_TECHNOLOGY, max_length=255)
    house_type = CharField(choices=HOUSE_TYPE, max_length=255)
    territory_type = CharField(choices=HOUSE_TERRITORY_TYPE, max_length=255)
    current_status = CharField(choices=HOUSE_CURRENT_STATUS, max_length=255)
    distance_to_sea = FloatField()
    registration_type = CharField(max_length=255, verbose_name='Оформление')
    invoice_type = CharField(choices=INVOICE_TYPE, max_length=255, verbose_name='Коммунальные платежи')
    invoice_options = CharField(max_length=255, verbose_name='Варианты расчёта')
    purpose = CharField(max_length=255, verbose_name='Назначение')
    contract_amount = CharField(max_length=255, verbose_name='Сумма в договоре')
    manager = ForeignKey(User, on_delete=CASCADE, blank=True, null=True)
    celling_height = FloatField(null=True)
    gas = BooleanField(default=False)
    heating = CharField(choices=HEATING_TYPE, null=True, max_length=255)
    water = CharField(choices=WATER_TYPE, max_length=255)


class Document(Model):
    file = FileField(upload_to='file/')
    house = ForeignKey(House, on_delete=CASCADE)


class HouseNews(Model):
    title = CharField(max_length=255, verbose_name='Заголовок новости')
    description = TextField(verbose_name='Описание новости')
    house = ForeignKey(House, on_delete=CASCADE, verbose_name='ЖК')


class Section(Model):
    house = ForeignKey(House, on_delete=CASCADE)
    name = CharField(max_length=255, verbose_name='Секция')


class Floor(Model):
    section = ForeignKey(Section, on_delete=CASCADE)
    name = CharField(max_length=255, verbose_name='Этаж')

    def __str__(self):
        return self.name


class Promotion(Model):
    PROMO_TYPE = (
        ('Большое объявление', 'Большое объявление'),
        ('Поднять объявление', 'Поднять объявление'),
        ('Турбо', 'Турбо'),
    )
    COLOR = (
        ('Красный', 'Красный'),
        ('Зелёный', 'Зелёный'),
        ('Синий', 'Синий'),
        ('Желтый', 'Желтый'),
    )
    PHRASE = (
        ('Подарок при покупке', 'Подарок при покупке'),
        ('Возможен торг', 'Возможен торг'),
        ('Квартира у моря', 'Квартира у моря'),
        ('В спальном районе', 'В спальном районе'),
        ('Вам повезло с ценой', 'Вам повезло с ценой'),
        ('Для большой семьи', 'Для большой семьи'),
        ('Семейное гнёздышко', 'Семейное гнёздышко'),
        ('Отдельная парковка', 'Отдельная парковка'),
    )

    type = CharField(choices=PROMO_TYPE, max_length=255, null=True)
    phrase = CharField(choices=PHRASE, max_length=255, null=True, verbose_name='Фраза')
    color = CharField(choices=COLOR, max_length=255, null=True)


class Apartment(Model):
    DOC_TYPE = (
        ('Документ собственности', 'Документ собственности'),
        ('Доверенность', 'Доверенность')
    )
    APART_TYPE = (
        ('Апартаменты', 'Апартаменты'),
        ('Пентхаус', 'Пентхаус')
    )
    APART_STATUS = (
        ('Черновая отделка', 'Черновая отделка'),
        ('Требует ремонта', 'Требует ремонта'),
        ('Требуется капитальный ремонт', 'Требуется капитальный ремонт'),
    )
    HEATING_TYPE = (
        ('Газовое', 'Газовое'),
        ('Дрова', 'Дрова')
    )
    SETTLEMENT_TYPE = (
        ('Мат. капитал', 'Мат. капитал'),
        ('Ипотека', 'Ипотека')
    )
    CONTACT_TYPE = (
        ('Звонок', 'Звонок'),
        ('Звонок + сообщение', 'Звонок + сообщение')
    )
    ADV_TYPE = (
        ('Первичный рынок', 'Первичный рынок'),
        ('Вторичный рынок', 'Вторичный рынок')
    )
    APART_CLASS = (
        ('Студия', 'Студия'),
        ('Студия, санузел', 'Студия, санузел')
    )

    house = ForeignKey(House, on_delete=CASCADE, null=True, verbose_name='ЖК')
    floor = ForeignKey(Floor, on_delete=CASCADE, blank=True, null=True, verbose_name='Этаж')
    document = CharField(choices=DOC_TYPE, max_length=255, verbose_name='Документ')
    room_count = IntegerField(verbose_name='Количество комнат')
    apartment_type = CharField(choices=APART_TYPE, max_length=255, verbose_name='Аппартаменты')
    apartment_status = CharField(choices=APART_STATUS, max_length=255, verbose_name='Жилое состояние')
    apartment_area = FloatField(verbose_name='Площадь квартиры')
    kitchen_area = FloatField(verbose_name='Площадь кухни')
    loggia = BooleanField(default=False, verbose_name='Балкон/лоджия')
    heating_type = CharField(choices=HEATING_TYPE, max_length=255)
    settlement_type = CharField(choices=SETTLEMENT_TYPE, max_length=255)
    contact = CharField(choices=CONTACT_TYPE, max_length=255)
    promotion = ForeignKey(Promotion, on_delete=CASCADE, blank=True, null=True)
    commission = IntegerField()
    description = TextField()
    price = IntegerField()
    main_image = ImageField(upload_to='image/')
    address = CharField(max_length=255)
    adv_type = CharField(choices=ADV_TYPE, max_length=255)
    apart_class = CharField(choices=APART_CLASS, max_length=255)
    is_actual = BooleanField(default=False)
    owner = ForeignKey(User, on_delete=CASCADE, verbose_name='Владелец объявления', blank=True, null=True)
    created_date = DateTimeField(auto_now=True, null=True)


class ApartImgRelations(Model):
    apart = ForeignKey(Apartment, on_delete=CASCADE)
    image = ImageField(upload_to='image/')


class UserApartRelation(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    apart = ForeignKey(Apartment, on_delete=CASCADE)


class Message(Model):
    sender = ForeignKey(User, on_delete=CASCADE, related_name='related_sender')
    recipient = ForeignKey(User, on_delete=CASCADE, related_name='related_recipient')
    text = TextField()
