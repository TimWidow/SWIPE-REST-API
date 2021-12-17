from datetime import datetime
from importlib import import_module

import pytz as pytz
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import *
from six import string_types
from phonenumber_field.serializerfields import PhoneNumberField
from . import auth
from .models import User, Promotion, Apartment, Floor, House, Section, Standpipe, HouseNew, HouseDoc, RequestToChess, \
    Block
from .verify import check


def import_callable(path_or_callable):
    if hasattr(path_or_callable, '__call__'):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, string_types)
        package, attr = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attr)


class RegistrationSerializer(ModelSerializer):
    password = CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    token = CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('phone', 'email', 'password', 'token',)

    def create(self, validated_data):
        print(validated_data)
        return User.objects.create_user(**validated_data)


class PhoneAuthenticationSerializer(Serializer):
    """
    Authenticates an existing user.
    Phone number is required.
    Returns a JSON web token.
    """

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    phone = PhoneNumberField(write_only=True)

    # Ignore these fields if they are included in the request.
    token = CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        phone = data.get('phone', None)

        if phone is None:
            raise ValidationError(
                'An phone number is required to log in.'
            )

        user = auth.PhoneAuthBackend.authenticate(phone=phone)

        if user is None:
            raise ValidationError(
                'A user with this phone number was not found.'
            )

        if not user.is_active:
            raise ValidationError(
                'This user has been deactivated.'
            )

        return {
            'user': user,
        }


class APILoginSerializer(Serializer):
    """
    Authenticates an existing user.
    Phone number is required.
    Returns a JSON web token.
    """
    email = EmailField(required=False, allow_blank=True)
    password = CharField(style={'input_type': 'password'})

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise ValidationError(msg)

        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            user = self._validate_email(email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    User.objects.get(email__iexact=email)
                except User.DoesNotExist:
                    pass

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            email_address = user.emailaddress_set.get(email=user.email)
            if not email_address.verified:
                raise ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs


class PhoneLoginSerializer(Serializer):
    """
    Authenticates an existing user.
    Phone number is required.
    Returns a JSON web token.
    """
    phone = PhoneNumberField(required=False, allow_blank=True)
    code = IntegerField(write_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    @staticmethod
    def _validate_phone(phone, code):

        if check(phone, code):
            user = User.objects.get(phone=phone)
        else:
            msg = _('Wrong code, try again')
            raise ValidationError(msg)

        return user

    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            user = self._validate_phone(phone, code)

        else:
            # Authentication without using allauth
            if phone:
                try:
                    User.objects.get(phone__iexact=phone)
                except User.DoesNotExist:
                    pass

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            email_address = user.emailaddress_set.get(email=user.email)
            if not email_address.verified:
                raise ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs


class UserDetailsSerializer(ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ('pk', 'phone', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class JWTSerializer(Serializer):
    """
    Serializer for JWT authentication.
    """
    token = CharField()
    user = SerializerMethodField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def get_user(self, obj):
        """
        Required to allow using custom USER_DETAILS_SERIALIZER in
        JWTSerializer. Defining it here to avoid circular imports
        """
        rest_auth_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})
        JWTUserDetailsSerializer = import_callable(
            rest_auth_serializers.get('USER_DETAILS_SERIALIZER', UserDetailsSerializer)
        )
        user_data = JWTUserDetailsSerializer(obj['user'], context=self.context).data
        return user_data


class PromotionSerializer(ModelSerializer):
    class Meta:
        model = Promotion
        fields = ('type', 'phrase', 'color')


class ApartmentListSerializer(ModelSerializer):
    promotion = PromotionSerializer()

    class Meta:
        model = Apartment
        fields = ('house', 'floor', 'rooms', 'apart_area')


class ApartmentDetailSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields = (
            'house', 'floor', 'document', 'address', 'rooms', 'apart_type', 'apart_status', 'apart_layout',
            'apart_area', 'kitchen_area', 'loggia', 'heating', 'client')


class ApartmentCreateSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['house', 'floor', 'rooms', 'document', 'apart_type', 'apart_status', 'apart_layout',
                  'apart_area', 'kitchen_area', 'loggia', 'heating']

    def create(self, validated_data):
        return Apartment.objects.create(**validated_data)


class FloorListSerializer(ModelSerializer):
    class Meta:
        model = Floor
        fields = ('section', 'number')


class FloorCreateSerializer(ModelSerializer):
    class Meta:
        model = Floor
        fields = ['section', 'number']

    def create(self, validated_data):
        return Floor.objects.create(**validated_data)


class ContactListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ContactCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'email', 'subscription_date',
                  'agent_first_name', 'agent_last_name', 'agent_phone', 'notifications']


class HouseListSerializer(ModelSerializer):
    class Meta:
        model = House
        fields = ['title', 'address']


class ContactSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class HouseDetailSerializer(ModelSerializer):
    manager = ContactSerializer()

    class Meta:
        model = House
        fields = '__all__'


class HouseDetailApartSerializer(ModelSerializer):
    floor = SerializerMethodField()

    class Meta:
        model = Apartment
        fields = ('house', 'floor', 'address', 'apart_area', 'rooms')

    @staticmethod
    def get_floor(obj):
        return obj.floor.number


class HouseSerializer(ModelSerializer):
    status_display = CharField(source='get_status_display', read_only=True)
    type_display = CharField(source='get_type_display', read_only=True)
    house_class_display = CharField(source='get_house_class_display', read_only=True)
    tech_display = CharField(source='get_tech_display', label='tech', read_only=True)
    territory_display = CharField(source='get_territory_display', read_only=True)
    gas_display = CharField(source='get_gas_display', read_only=True)
    heating_display = CharField(source='get_heating_display', read_only=True)
    electricity_display = CharField(source='get_electricity_display', read_only=True)
    sewerage_display = CharField(source='get_sewerage_display', read_only=True)
    water_supply_display = CharField(source='get_water_supply_display', read_only=True)
    communal_payments_display = CharField(source='get_communal_payments_display', read_only=True)
    completion_display = CharField(source='get_completion_display', read_only=True)
    payment_options_display = CharField(source='get_payment_options_display', read_only=True)
    role_display = CharField(source='get_role_display', read_only=True)
    sum_in_contract_display = CharField(source='get_sum_in_contract_display', read_only=True)

    # Apartments = HouseDetailApartSerializer(read_only=True, many=True)
    block_count = SerializerMethodField()
    section_count = SerializerMethodField()
    floor_count = SerializerMethodField()

    # Apartment_count = SerializerMethodField()

    class Meta:
        model = House
        fields = '__all__'

    @staticmethod
    def get_block_count(obj):
        return Block.objects.filter(house=obj).count()

    @staticmethod
    def get_section_count(obj):
        return Section.objects.filter(block__house=obj).count()

    @staticmethod
    def get_floor_count(obj):
        return Floor.objects.filter(section__block__house=obj).count()

    @staticmethod
    def get_apart_count(obj):
        return Apartment.objects.filter(floor__section__block__house=obj).count()


class StandpipeSerializer(ModelSerializer):
    id = IntegerField(required=False)

    class Meta:
        model = Standpipe
        fields = ('id', 'number',)


class SectionSerializer(ModelSerializer):
    pipes = StandpipeSerializer(many=True, required=False)
    full_name = SerializerMethodField()
    house = SerializerMethodField()
    has_related = SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'number', 'block', 'pipes', 'full_name', 'house', 'has_related')

    @staticmethod
    def get_has_related(obj):
        return obj.floors.exists()

    @staticmethod
    def get_house(obj):
        return obj.block.house.pk

    @staticmethod
    def get_full_name(obj):
        return f'Секция №{obj.number}. Корпус №{obj.block.number}'

    def create(self, validated_data):
        next_number = Section.get_next(validated_data.get('block'))
        validated_data['number'] = next_number
        if validated_data.get('pipes'):
            pipes_data = validated_data.pop('pipes')
            section = Section.objects.create(**validated_data)
            for pipe_data in pipes_data:
                Standpipe.objects.create(section=section, **pipe_data)
        else:
            section = Section.objects.create(**validated_data)
        return section

    def update(self, instance, validated_data):
        pipes_data = None
        if validated_data.get('pipes'):
            pipes_data = validated_data.pop('pipes')
        instance = super().update(instance, validated_data)
        if pipes_data:
            for pipe_data in pipes_data:
                pipe = get_object_or_404(Standpipe, pk=pipe_data.get('id'))
                pipe.name = pipe_data.get('name')
                pipe.save()
        return instance


class FloorSerializer(ModelSerializer):
    full_name = SerializerMethodField()
    house = SerializerMethodField()
    has_related = SerializerMethodField()

    class Meta:
        model = Floor
        fields = '__all__'

    @staticmethod
    def get_has_related(obj):
        return obj.aparts.exists()

    @staticmethod
    def get_house(obj):
        return obj.section.block.house.pk

    @staticmethod
    def get_full_name(obj):
        block = obj.section.block
        return f'Этаж №{obj.number}. Секция №{obj.section.number}. Корпус №{block.number}'

    def create(self, validated_data):
        next_number = Floor.get_next(validated_data.get('block'))
        inst = Floor.objects.create(number=next_number, section=validated_data.get('section'))
        return inst


class HouseNewSerializer(ModelSerializer):
    created = SerializerMethodField()

    class Meta:
        model = HouseNew
        fields = '__all__'

    @staticmethod
    def get_created(obj):
        return f'{obj.created.year}-{obj.created.month}-{obj.created.day}'


class HouseDocSerializer(ModelSerializer):
    class Meta:
        model = HouseDoc
        fields = ('id', 'file', 'house')


class ApartSerializer(ModelSerializer):
    state_display = CharField(source='get_state_display', read_only=True)
    foundation_doc_display = CharField(source='get_foundation_doc_display', read_only=True)
    type_display = CharField(source='get_type_display', read_only=True)
    plan_display = CharField(source='get_plan_display', read_only=True)
    balcony_display = CharField(source='get_balcony_display', read_only=True)

    floor_display = SerializerMethodField()
    house_pk = SerializerMethodField()
    sales_department_pk = SerializerMethodField()

    class Meta:
        model = Apartment
        fields = '__all__'

    @staticmethod
    def get_sales_department_pk(obj):
        try:
            return obj.user.pk
        except Exception as error:
            print(error)

    @staticmethod
    def get_floor_display(obj):
        print(obj)
        try:
            floor = obj.floor
            section = floor.section
            block = section.block
            return f"Корпус {block.number}, Секция {section.number}, Этаж {floor.number}"
        except Exception as error:
            print(error)

    @staticmethod
    def get_house_pk(obj):
        try:
            return obj.floor.section.block.house.pk
        except Exception as error:
            print(error)

class HouseInRequestSerializer(ModelSerializer):
    role_display = CharField(source='get_role_display', read_only=True)

    class Meta:
        model = House
        fields = ('name', 'address', 'role', 'city', 'role_display')


class ApartInRequestSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields = ('pk', 'number', 'floor', 'booked', 'client')


class RequestToChessSerializer(ModelSerializer):
    apart_display = SerializerMethodField()

    class Meta:
        model = RequestToChess
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created'] = datetime.now(tz=pytz.UTC)
        return super().create(validated_data)

    @staticmethod
    def get_apart_display(obj):
        apart = obj.apart
        if apart.client:
            client = obj.apart.client
            return {
                'id': apart.pk,
                'number': apart.number,
                'floor': f'Корпус {apart.floor.section.block.number}, ' /
                         f'Секция {apart.floor.section.number}, ' /
                         f'Этаж {apart.floor.number}',
                'house': apart.floor.section.block.house,
                'house_pk': apart.floor.section.block.house.pk,
                'client_pk': client.pk,
                'client_full_name': client.full_name(),
                'client_phone_number': client.phone_number,
                'client_email': client.email
            }
        return {}

    def update(self, instance, validated_data):
        apart = instance.apart
        apart.owned = validated_data['approved']
        apart.booked = validated_data['approved']
        if not validated_data['approved']:
            apart.client = None
        apart.save()
        return super().update(instance, validated_data)
