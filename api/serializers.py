from django.contrib.auth import authenticate
from . import auth

from . import models
from rest_framework import serializers
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Creates a new user.
    Email, username, and password are required.
    Returns a JSON web token.
    """

    # The password must be validated and should not be read by the client
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'token',)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """
    phone = serializers.IntegerField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    # Ignore these fields if they are included in the request.
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        phone = data.get('phone', None)
        password = data.get('password', None)

        if phone is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = auth.PhoneAuthBackend.authenticate(phone=phone, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Promotion
        fields = ('type', 'phrase', 'color')


class ApartmentListSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer()

    class Meta:
        model = models.Apartment
        fields = ('id', 'main_image', 'promotion', 'price', 'address', 'created_date', 'room_count', 'apartment_area',
                  'promotion', 'house', 'floor')


class ApartmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apartment
        fields = ('id', 'main_image', 'price', 'address', 'adv_type', 'apartment_status', 'apartment_type', 'apart_class',
                  'apartment_area', 'kitchen_area', 'loggia', 'heating_type', 'settlement_type', 'commission',
                  'description', 'owner', 'promotion')


class ApartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apartment
        fields = ['address', 'floor', 'price', 'document', 'apartment_type', 'room_count', 'apart_class',
                  'apartment_status', 'apartment_area', 'kitchen_area', 'loggia', 'heating_type', 'commission',
                  'description', 'owner']

    def create(self, validated_data):
        return models.Apartment.objects.create(**validated_data)



class FloorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Floor
        fields = ('section', 'name')


class FloorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Floor
        fields = ['id', 'section', 'name']

    def create(self, validated_data):
        return models.Floor.objects.create(**validated_data)


class ContactListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ['id', 'user', 'first_name', 'last_name']


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'subscribe_expired', 'subscribe', 'agent_first_name',
                  'agent_last_name', 'notification']


class HouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.House
        fields = ['id', 'address']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = '__all__'


class HouseDetailSerializer(serializers.ModelSerializer):
    manager = ContactSerializer()

    class Meta:
        model = models.House
        fields = '__all__'




