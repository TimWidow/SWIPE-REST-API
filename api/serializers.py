from django.shortcuts import get_object_or_404
from rest_framework.serializers import *
from . import auth

from .models import User, House, Promotion, Apartment, Floor, Section, HouseNew, HouseDoc, Standpipe


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
        validated_data['username'] = validated_data['email']
        print(validated_data)
        return User.objects.create_user(**validated_data)


class LoginSerializer(Serializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    phone = IntegerField(write_only=True)
    password = CharField(max_length=128, write_only=True)

    # Ignore these fields if they are included in the request.
    token = CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        phone = data.get('phone', None)
        password = data.get('password', None)

        if phone is None:
            raise ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise ValidationError(
                'A password is required to log in.'
            )

        user = auth.PhoneAuthBackend.authenticate(phone=phone)

        if user is None:
            raise ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }


class PromotionSerializer(ModelSerializer):
    class Meta:
        model = Promotion
        fields = ('type', 'phrase', 'color')


class ApartmentListSerializer(ModelSerializer):
    promotion = PromotionSerializer()

    class Meta:
        model = Apartment
        fields = ('house', 'floor', 'rooms', 'apart_area', 'price', 'created', 'promotion')


class ApartmentDetailSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields = (
            'house', 'floor', 'document', 'address', 'rooms', 'apart_type', 'apart_status', 'apart_layout',
            'apart_area', 'kitchen_area', 'loggia', 'heating', 'payment', 'contact', 'promotion',
            'commission', 'description', 'price', 'owner')


class ApartmentCreateSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['house', 'floor', 'rooms', 'document', 'apart_type', 'apart_status', 'apart_layout',
                  'apart_area', 'kitchen_area', 'loggia', 'heating', 'commission', 'description', 'owner']

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
        fields = ('number', 'square', 'floor', 'client', 'booked')

    @staticmethod
    def get_floor(obj):
        return obj.floor.name


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

    flats = HouseDetailApartSerializer(read_only=True, many=True)
    building_count = SerializerMethodField()
    section_count = SerializerMethodField()
    floor_count = SerializerMethodField()
    flat_count = SerializerMethodField()

    class Meta:
        model = House
        fields = '__all__'
    
    @staticmethod
    def get_building_count(obj):
        return obj.buildings.count()

    @staticmethod
    def get_section_count(obj):
        return Section.objects.filter(building__house=obj).count()

    @staticmethod
    def get_floor_count(obj):
        return Floor.objects.filter(section__building__house=obj).count()

    @staticmethod
    def get_flat_count(obj):
        return Apartment.objects.filter(floor__section__building__house=obj).count()

class BuildingSerializer(ModelSerializer):
    full_name = SerializerMethodField()
    has_related = SerializerMethodField()

    class Meta:
        model = Building
        fields = '__all__'

    def get_has_related(self, obj):
        return obj.sections.exists()

    def get_full_name(self, obj):
        return f'Корпус №{obj.number}'

    def create(self, validated_data):
        next_number = Building.get_next(validated_data.get('house'))
        inst = Building.objects.create(number=next_number, house=validated_data.get('house'))
        return inst


class StandpipeSerializer(ModelSerializer):
    id = IntegerField(required=False)

    class Meta:
        model = Standpipe
        fields = ('id', 'name', )


class SectionSerializer(ModelSerializer):
    pipes = StandpipeSerializer(many=True, required=False)
    full_name = SerializerMethodField()
    house = SerializerMethodField()
    has_related = SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'number', 'building', 'pipes', 'full_name', 'house', 'has_related')

    def get_has_related(self, obj):
        return obj.floors.exists()

    def get_house(self, obj):
        return obj.building.house.pk

    def get_full_name(self, obj):
        return f'Секция №{obj.number}. Корпус №{obj.building.number}'

    def create(self, validated_data):
        next_number = Section.get_next(validated_data.get('building'))
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

    def get_has_related(self, obj):
        return obj.flats.exists()

    def get_house(self, obj):
        return obj.section.building.house.pk

    def get_full_name(self, obj):
        building = obj.section.building
        return f'Этаж №{obj.number}. Секция №{obj.section.number}. Корпус №{building.number}'

    def create(self, validated_data):
        next_number = Floor.get_next(validated_data.get('building'))
        inst = Floor.objects.create(number=next_number, section=validated_data.get('section'))
        return inst


class NewsItemSerializer(ModelSerializer):
    created = SerializerMethodField()

    class Meta:
        model = HouseNew
        fields = '__all__'

    def get_created(self, obj):
        return f'{obj.created.year}-{obj.created.month}-{obj.created.day}'


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = HouseDoc
        fields = ('id', 'file', 'house')


class FlatSerializer(ModelSerializer):
    state_display = CharField(source='get_state_display', read_only=True)
    foundation_doc_display = CharField(source='get_foundation_doc_display', read_only=True)
    type_display = CharField(source='get_type_display', read_only=True)
    plan_display = CharField(source='get_plan_display', read_only=True)
    balcony_display = CharField(source='get_balcony_display', read_only=True)

    floor_display = SerializerMethodField()
    house_pk = SerializerMethodField()
    sales_department_pk = SerializerMethodField()

    class Meta:
        model = Flat
        fields = '__all__'

    def get_sales_department_pk(self, obj):
        return obj.user.pk

    def get_floor_display(self, obj):
        floor = obj.floor
        section = floor.section
        building = section.building
        return f'Корпус {building.number}, Секция {section.number}, Этаж {floor.number}'

    def get_house_pk(self, obj):
        return obj.floor.section.building.house.pk


class HouseInRequestSerializer(ModelSerializer):
    role_display = CharField(source='get_role_display', read_only=True)

    class Meta:
        model = House
        fields = ('name', 'address', 'role', 'city', 'role_display')


class FlatInRequestSerializer(ModelSerializer):
    class Meta:
        model = Flat
        fields = ('pk', 'number', 'floor', 'booked', 'client')


class RequestToChestSerializer(ModelSerializer):
    flat_display = SerializerMethodField()

    class Meta:
        model = RequestToChest
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created'] = datetime.datetime.now(tz=pytz.UTC)
        return super().create(validated_data)

    def get_flat_display(self, obj):
        flat = obj.flat
        if flat.client:
            client = obj.flat.client
            return {
                'id': flat.pk,
                'number': flat.number,
                'floor': _('Корпус {building}, Секция {section}, Этаж {floor}').format(building=flat.floor.section.building.number,
                                                                                       section=flat.floor.section.number,
                                                                                       floor=flat.floor.number),
                'house': flat.floor.section.building.house.name,
                'house_pk': flat.floor.section.building.house.pk,
                'client_pk': client.pk,
                'client_full_name': client.full_name(),
                'client_phone_number': client.phone_number,
                'client_email': client.email
            }
        return {}

    def update(self, instance, validated_data):
        flat = instance.flat
        flat.owned = validated_data['approved']
        flat.booked = validated_data['approved']
        if not validated_data['approved']:
            flat.client = None
        flat.save()
        return super().update(instance, validated_data)
