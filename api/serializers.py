from . import auth
from rest_framework import serializers
from phone_verify.serializers import SMSVerificationSerializer
from .models import User, House, Promotion, Apartment, Floor


class RegistrationSerializer(serializers.ModelSerializer, SMSVerificationSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('phone', 'email', 'password', 'token',)

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        print(validated_data)
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer, SMSVerificationSerializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

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
        model = Promotion
        fields = ('type', 'phrase', 'color')


class ApartmentListSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer()

    class Meta:
        model = Apartment
        fields = ('house', 'floor', 'rooms', 'apart_area', 'price', 'created', 'promotion')


class ApartmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = (
            'house', 'floor', 'rooms', 'apart_type', 'apart_status', 'apart_layout',
            'apart_area', 'kitchen_area', 'loggia', 'heating', 'payment', 'price', 'commission',
            'description', 'owner', 'promotion')


class ApartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['house', 'floor', 'rooms', 'document', 'apart_type', 'apart_status', 'apart_layout',
                  'apart_area', 'kitchen_area', 'loggia', 'heating', 'commission', 'description', 'owner']

    def create(self, validated_data):
        return Apartment.objects.create(**validated_data)


class FloorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('section', 'number')


class FloorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ['section', 'number']

    def create(self, validated_data):
        return Floor.objects.create(**validated_data)


class ContactListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'email', 'subscription_date',
                  'agent_first_name', 'agent_last_name', 'agent_phone', 'notifications']


class HouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ['title', 'address']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class HouseDetailSerializer(serializers.ModelSerializer):
    manager = ContactSerializer()

    class Meta:
        model = House
        fields = '__all__'
